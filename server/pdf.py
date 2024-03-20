import fitz
import json
import os
import pandas as pd
import time

class PDFObject:
    def __init__(self,pdf_path):
        start_time=time.time()
        
        self.pdf_path=pdf_path
        self.doc=fitz.open(pdf_path)
        self.pages=[]
        self.dataframe=None
        self._parse_raw()
        self.generate_dataframe()
        # self.dataframe = self.dataframe.dropna()
        self.size_clustering_by_font()
        
        self.init_time=time.time()-start_time
        print(f'init time: {self.init_time} seconds')
        
        
    def _parse_raw(self):
        for index, page in enumerate(self.doc):
            self.pages.append(PageObject(page))
    def get_pages(self):
        return self.pages
    def get_text(self):
        return [page.get_text() for page in self.pages]
    def get_font(self):
        return [page.get_font() for page in self.pages]
    def generate_dataframe(self):
        dataframe_list=[]
        for index, page in enumerate(self.pages):
            df_temp=page.get_dataframe()
            df_temp['page_no']=index+1
            df_temp['string_length']=df_temp['text'].apply(lambda x: len(x))
            dataframe_list.append(df_temp)
            
        self.dataframe=pd.concat(dataframe_list)
        # 去重，bbox由于unhashable所以去掉，但其他信息也够了
        self.dataframe=self.dataframe.drop_duplicates(subset=self.dataframe.columns.difference(['bbox']))

    def _clustering(self, df, threshold=0.2):
        clusters = []  # 保存最终的类别标签
        centers = []   # 保存每个类的中心值

        # 将第一个数据点作为第一个类的中心
        clusters.append(df.iloc[0])
        centers.append(df.iloc[0])

        # 遍历剩余的数据点，根据阈值将其分配到类别，并更新类中心
        for row in df.iloc[1:]:
            assigned = False  # 标记是否已经分配给某个类别
            for  center in centers:
                if abs(row - center) <= threshold:
                    clusters.append(center)
                    assigned = True
                    break
            if not assigned:
                clusters.append(row)
                centers.append(row)

        return clusters

    def size_clustering_by_font(self, threshold=0.2):
        unique_font = self.dataframe['font'].unique()
        for font in unique_font:
            df = self.dataframe[self.dataframe['font'] == font]
            clusters = self._clustering(df['size'], threshold)
            
            # self.dataframe[self.dataframe['font'] == font]['size'] = clusters
            self.dataframe.loc[self.dataframe['font'] == font, 'size'] = clusters

        # self.dataframe['font']=round(self.dataframe['font'],2)
        
        
        # self.dataframe.dropna(inplace=True)

    def size_with_fonts(self):
        return_obj = {}
        df=self.dataframe
        df=df[['size','font']].drop_duplicates()
        df['size']=df['size'].apply(lambda x: [str(x)])
        df=df.groupby('font').agg({'size':'sum'}).reset_index()
        temp_list=df.to_dict(orient='records')
        return_obj['list']=temp_list
        
        recommend_dict=self.dataframe.groupby(['size','font']).agg({'string_length':'sum'}).reset_index().sort_values('string_length',ascending=False).to_dict(orient='records')
        for index,i in enumerate(recommend_dict):
            recommend_dict[index]['size']=str(i['size'])
        return_obj['recommend']=recommend_dict
        return return_obj
    
    # def filter_by_size_and_font(self,list_of_size_font):
    #     # Not used
    #     return self.dataframe[self.dataframe.apply(lambda x: (str(x['size']),x['font']) in list_of_size_font,axis=1)]

    def compact_strings_by_block(self,df):
        custom_join_with_space = lambda column: ' '.join(column)
        return df.groupby(['page_no','block_num']).agg({'text':custom_join_with_space}).reset_index().sort_values(['page_no','block_num'],ascending=True)
    
    def get_bboxes(self):
        return_obj= self.dataframe[['size','font','page_no','bbox','page_size']].to_dict(orient='records')
        for index, i in enumerate(return_obj):
            return_obj[index]['size']=str(i['size'])
        return return_obj

    def get_merged_text_by_size_font(self,obj):
        '''
        Merged by page_no and block_num
        '''
        custom_join_with_space = lambda column: ' '.join(column)
        return self.dataframe[self.dataframe.apply(lambda x: {'size':str(x['size']),'font':x['font']} in obj,axis=1)].groupby(['page_no','block_num']).agg({'text':custom_join_with_space}).reset_index().sort_values(['page_no','block_num'],ascending=True)

class PageObject:
    def __init__(self,page):
        self._parse_raw(page)
        self.dataframe_list=[]
        self.dataframe=None
        self.get_dataframe()
        
    def _parse_raw(self,page):
        textpage=page.get_textpage()
        textdict=textpage.extractRAWDICT()
        self.width=textdict['width']
        self.height=textdict['height']
        self.block_list=[]
        for block in textdict['blocks']:
            self.block_list.append(BlockObject(block))
    def get_font(self):
        font_list=[item for k in self.block_list for item in k.get_font() ]
        font_list=list(set(font_list))
        return font_list
    def get_dataframe(self):
        for block in self.block_list:
            for line in block.lines:
                for span in line.spans:
                    self.dataframe_list.append(span.info()+[block.number]+[(self.width,self.height)])
        return pd.DataFrame(self.dataframe_list,columns=['text','font','size','bbox','flags','block_num','page_size'])

class BlockObject:
    def __init__(self,block):
        self._parse_raw(block)
    def _parse_raw(self,block):
        self.number=block['number']
        self.type=block['type']
        self.bbox=block['bbox']
        self.lines=[]
        for line in block['lines']:
            self.lines.append(LineObject(line))
    def get_font(self):
        font_list=[item for k in self.lines for item in k.get_font() ]
        font_list=list(set(font_list))
        return font_list

class LineObject:
    def __init__(self,line):
        self._parse_raw(line)
    def _parse_raw(self,line):
        self.bbox=line['bbox']
        self.wmode=line['wmode']
        self.dir=line['dir']
        self.spans=[]
        for span in line['spans']:
            self.spans.append(SpanObject(span))
    def get_font(self):
        font_list=[k.get_font() for k in self.spans]
        font_list=list(set(font_list))
        return font_list

class SpanObject:
    def __init__(self,span):
        self._parse_raw(span)
    def _parse_raw(self,span):
        self.size=span['size']
        self.size=round(self.size,2)
        
        self.flags=span['flags']
        self.font=span['font']
        self.color=span['color']
        self.ascender=span['ascender']
        self.descender=span['descender']
        self.origin=span['origin']

        self.bbox=span['bbox']
        self.bbox=[round(k,2) for k in self.bbox]
        
        self.chars_str=''.join([k['c'] for k in span['chars']])
    
    def get_text(self):
        return self.chars_str
    def get_font(self):
        return self.font
    def get_size(self):
        return self.size
    
    def info(self):
        return [self.get_text(),self.get_font(),self.get_size(),self.bbox,self.flags]


if __name__=='__main__':
    pdf_path=r"D:\git_download\read-aloud\1706.03762.pdf"
    pdf=PDFObject(pdf_path)
    # print(pdf.dataframe.head(10))
    # pdf.size_with_fonts()
    
    nan_rows=pdf.dataframe.isna().any(axis=1)
    with open('nan_rows.csv','w',encoding='utf-8') as f:
        f.write(pdf.dataframe[nan_rows].to_csv(index=False))
    
    # with open('size_with_fonts.json','w',encoding='utf-8') as f:
    #     f.write(json.dumps(pdf.size_with_fonts(),indent=4))
    
#     with open('compact_strings_by_block.txt','w',encoding='utf-8') as f:
#         f.write(json.dumps(pdf.compact_strings_by_block(pdf.filter_by_size_and_font(
#     [
#         (9.96,'NimbusRomNo9L-Regu'),
#         (8.88,'NimbusRomNo9L-Regu'),    
#     ]
# ))['text'].to_list(),indent=4,ensure_ascii=False))
    # with open('temp.txt','w',encoding='utf-8') as f:
    #     f.write(
    #         json.dumps(pdf.size_with_fonts(),indent=4)
    #     )
    
    with open('raw_pdf.txt','w',encoding='utf-8') as f:
        f.write(json.dumps(pdf.doc[6].get_textpage().extractRAWDICT(),indent=4))