import os,sys,json
config_path=os.path.join(os.path.dirname(__file__),'config.json')
with open(config_path,'r',encoding='utf-8') as f:
    config=json.load(f)
GPTSOVITS_BASE=config['GPTSOVITS_BASE']
server_port=config['server_port']

sys.path.append(GPTSOVITS_BASE)
os.chdir(GPTSOVITS_BASE)

from inference_webui_copy import get_tts_wav,i18n,change_sovits_weights,change_gpt_weights
import soundfile as sf
import json,os
import time
import requests

# print(type(i18n))

zh=i18n("中文")
zh_en=i18n("中英混合")


def change_weight(gpt_weight,sovits_weight):
    change_gpt_weights(gpt_weight)
    change_sovits_weights(sovits_weight)


def voice_inference(
    ref_wav_path, prompt_text, prompt_language, text, text_language,output_file_path
):
    print(f'time before inference: {time.time()}')
    # 调用函数获取生成器
    generator = get_tts_wav(ref_wav_path, prompt_text, prompt_language, text, text_language)

    print(f'time after inference: {time.time()}')
    
    # 遍历生成器，获取音频数据
    for sampling_rate, audio_data in generator:
        print(f'time after generator: {time.time()}')
        
        # 这里可以对音频数据进行处理，或者直接保存为文件
        # 例如：
        # 对音频进行处理
        processed_audio_data = audio_data
        sf.write(output_file_path, processed_audio_data, sampling_rate, format="wav")
        print("音频已保存为文件:", output_file_path)
        print(f'time after save: {time.time()}')
        break  # 这里我们只处理第一个生成的音频，如果需要处理全部生成的音频，可以移除这行break


if __name__=='__main__':
    with open(os.path.join(os.path.dirname(__file__),'data.json'),'r',encoding='utf-8') as f:
        obj=json.load(f)
    
    signal_url=f'http://localhost:{server_port}/finished_one_inference'
    
    for index1, item in enumerate(obj):
        change_weight(item['gpt_weight'],item['sovits_weight'])
        for index2,line in enumerate(item['lines']):
            voice_inference(
                line['ref_wav_path'],
                line['prompt_text'],
                i18n(line['prompt_language_text']),
                line['text'],
                i18n(line['text_language_text']),
                line['output_file_path']
            )
            print('done_here')
            # connect to backend
            res=requests.post(signal_url,json={
                'output_file_path':line['output_file_path'],
                'if_end':index1==len(obj)-1 and index2==len(item['lines'])-1,
            })
            json_data=res.json()
            if json_data['should_interrupt']:
                exit(0)
    exit(0)