<script>
import axios from 'axios';

export default {
    data() {
        return {
            page_max_no: 0,
            raw_filtered_text: [],

            filtered_text: [],
            shown_text_length: 15,
            zfill_bits: 4,
            page_select_input_string: '',
            page_select_list: [],

            text_minlength_filter: 200,
            text_minlength_filter_text: '',

            gpt_selected: '',
            sovits_selected: '',
            language_selected: '',
            raw_candidate_weights: {},
            languange_candidates: [],
            relative_speed: 0.6,

            default_infer_language: '',
            default_gpt_weight: '',
            default_sovits_weight: '',
        }
    },
    mounted() {
        // this.get_filtered_text()
        this.get_candidate_weights()
        this.language_candidate_init()
        // this.page_select()
        // this.refresh_block_class()
    },
    methods: {
        path_basename(path) {
            if (path.includes('/')) {
                path = path.split('/')
                path = path[path.length - 1]
            }
            if (path.includes('\\')) {
                path = path.split('\\')
                path = path[path.length - 1]
            }
            return path
        },
        generate_page_id(page_no) {
            return 'page_no-' + this.zfill(page_no, this.zfill_bits)
        },
        generate_block_id(page_no, block_num) {
            return 'page_no-' + this.zfill(page_no, this.zfill_bits) + '-block_num-' + this.zfill(block_num, this.zfill_bits)
        },
        parse_block_id(block_id) {
            // console.log(block_id)
            let str1 = block_id.split('page_no-')[1]
            let list2 = str1.split('-block_num-').map(item => Number(item))
            return list2
        },
        zfill(number, width) {
            let numStr = String(number);
            let diff = width - numStr.length;
            if (diff > 0) {
                return '0'.repeat(diff) + numStr;
            } else {
                return numStr;
            }
        },
        index_query_list_of_obj_by_attr(list, attr, value) {
            for (let i = 0; i < list.length; i++) {
                if (list[i][attr] == value) {
                    return i;
                }
            }
            return -1;
        },

        get_filtered_text() {
            // render the list items
            const path = this.BACKENDPATH + '/get_filtered_text';
            axios.get(path)
                .then((response) => {
                    this.page_max_no = response.data['page_max_no']
                    this.raw_filtered_text = response.data['text'];
                    this.default_infer_language = response.data['default_infer_language']
                    this.default_gpt_weight = response.data['default_gpt_weight']
                    this.default_sovits_weight = response.data['default_sovits_weight']

                    this.filtered_text = [];
                    for (let i = 0; i < this.raw_filtered_text.length; i++) {
                        let index = this.index_query_list_of_obj_by_attr(this.filtered_text, 'page_no', this.raw_filtered_text[i].page_no);
                        if (index == -1) {
                            this.filtered_text.push({
                                'page_no': this.raw_filtered_text[i].page_no,
                                // 'chosen':true,
                                'blocks': [
                                    {
                                        'block_num': this.raw_filtered_text[i].block_num,
                                        'text': this.raw_filtered_text[i].text.replace(/\n/g, " ")
                                    }
                                ]
                            });
                        } else {
                            this.filtered_text[index].blocks.push({
                                'block_num': this.raw_filtered_text[i].block_num,
                                'text': this.raw_filtered_text[i].text.replace(/\n/g, " ")
                            });
                        }

                    }
                    // console.log(this.filtered_text);
                    this.page_select()
                }).then(
                    this.refresh_block_class()
                )
                .catch((error) => {
                    console.log(error);
                });
        },
        get_candidate_weights() {
            const path = this.BACKENDPATH + '/candidate_weights';
            axios.get(path)
                .then(
                    (response) => {
                        this.raw_candidate_weights = response.data
                    }
                ).catch(
                    err => console.log(err)
                )
        },
        language_candidate_init() {
            this.languange_candidates = [
                "中文",
                "英文",
                "日文",
                "中英混合",
                "日英混合",
                "多语种混合",
            ]
        },

        page_select() {
            // Parsing input select string
            console.log('this.page_select_input_string', this.page_select_input_string)

            let temp = this.page_select_input_string.split(',')
            temp = temp.filter(item => item != '')
            this.page_select_list = []

            if (temp.length === 0) {
                for (let i = 1; i <= this.page_max_no; i++) {
                    this.page_select_list.push(i)
                }
                console.log('here')
                this.refresh_page_class()
                return
            }

            for (let i = 0; i < temp.length; i++) {
                // 1 or 2 or 3
                if (temp[i].length == 1) {
                    let num = Number(temp[i][0])
                    if (1 <= num && num <= this.page_max_no) this.page_select_list.push(num)
                    continue
                }

                // -1 or 2- or 1-3
                let elem_temp = temp[i].split('-')
                if (elem_temp.length != 2 || Number(elem_temp[0]) == NaN || Number(elem_temp[1]) == NaN) {
                    this.page_select_list = []

                    this.refresh_page_class()
                    return
                }
                if (elem_temp[0] != '' && elem_temp[1] != '') {
                    for (let j = Number(elem_temp[0]); j <= Number(elem_temp[1]); j++)this.page_select_list.push(j)
                }
                else if (elem_temp[0] == '' && i == 0) {
                    for (let j = 0; j <= Number(elem_temp[1]); j++)this.page_select_list.push(j)
                }
                else if (elem_temp[1] == '' && i == temp.length - 1) {
                    for (let j = Number(elem_temp[0]); j <= this.page_max_no; j++)this.page_select_list.push(j)
                }
                else {
                    this.page_select_list = []

                    this.refresh_page_class()
                    return
                }
            }
            this.page_select_list = [...new Set(this.page_select_list)]
            this.refresh_page_class()
            return
        },
        refresh_page_class() {
            // Changing the classes
            const container = window.parent.document.getElementById('voice-controls-textlist-container')
            const page_elem_list = container.getElementsByClassName('page_elem')
            // console.log(page_elem_list.length,'page_elem_list')
            const candidate_page_id_list = this.page_select_list.map(item => this.generate_page_id(item))
            for (let i = 0; i < page_elem_list.length; i++) {
                if (candidate_page_id_list.includes(page_elem_list[i].id)) {
                    page_elem_list[i].classList.add('page_chosen')
                } else {
                    page_elem_list[i].classList.remove('page_chosen')
                }
            }
            // console.log(this.page_select_list)
        },
        minlength_input_func() {
            this.text_minlength_filter = this.text_minlength_filter >= 0 ? this.text_minlength_filter : 0
            this.refresh_block_class()
        },
        refresh_block_class() {
            console.log(this.text_minlength_filter)
            // Refresh by minlength filter
            const container = document.getElementById('voice-controls-textlist-container')
            const block_elem_list = container.getElementsByClassName('block_elem')
            for (let i = 0; i < block_elem_list.length; i++) {
                let temp_id = block_elem_list[i].id
                let [page_no, block_num] = [...this.parse_block_id(temp_id)]
                let index1 = this.index_query_list_of_obj_by_attr(this.filtered_text, 'page_no', page_no)
                let index2 = this.index_query_list_of_obj_by_attr(this.filtered_text[index1].blocks, 'block_num', block_num)
                let string_length = this.filtered_text[index1].blocks[index2].text.length
                if (string_length < this.text_minlength_filter) {
                    block_elem_list[i].classList.add('invisible')
                }
                else {
                    block_elem_list[i].classList.remove('invisible')
                }
            }
        },
        generate_post() {

            const path = this.BACKENDPATH + '/generate_post';
            let obj = {
                'minlength': this.text_minlength_filter,
                'page_selected': this.page_select_list,
                'gpt_weight': this.gpt_selected,
                'sovits_weight': this.sovits_selected,
                'languange_selected': this.language_selected,
                'relative_speed': this.relative_speed,
            }
            axios.post(path, obj)
                .then(
                    (response) => {
                        console.log(response)
                    }
                )
                .catch(
                    (err) => console.log(err)
                )
        },
        refresh_controls() {
            this.get_filtered_text()
            this.page_select()
        },
        interrupt_this_inference() {
            const path = this.BACKENDPATH + '/set_interrupt';
            axios.get(path)
                .then(
                    (response) => {
                        console.log(response)
                    }
                )
                .catch(
                    (err) => console.log(err)
                )
        },
        clear_voice_output() {
            const path = this.BACKENDPATH + '/clear_voice_output';
            axios.get(path)
                .then(
                    (response) => {
                        console.log(response)
                    }
                )
                .catch(
                    (err) => console.log(err)
                )
        },
    }

}
</script>


<!-- 
    下拉选择框，选择两种权重
    下拉选择框，选择输出语言
    勾选需要生成的pdf page no

    中断按钮——执行脚本每一轮循环像后端发送请求，如果需要中断则中断

    // 后端的自己的：文件系统管理

    向前端返回音频文件

    前端：定时向后端询问，并加载未加载的音频文件

    重新生成某一段——后端

    ——————————

    因此，后端的函数单元为：

 -->
<template>

    <div class="voice-controls" id="voice-controls">
        <div>

            <button type="button" class="custom-button" @click="refresh_controls" style="width: 40%;">
                刷新筛选结果
            </button>

            <input type="text" placeholder="输入页号 eg: -1,2-3,4,5-" v-model="page_select_input_string"
                @input="page_select" @focus="refresh_block_class" style="width: 50%;" />
        </div>


        <div id="voice-minlength-container">
            <div>

                <p>筛选每个block内的文本需不少于</p>
            </div>
            <input type="number" placeholder="输入整数" v-model="text_minlength_filter" @input="minlength_input_func"
                style="width: 60px;">
            <div>

                <p>个字</p>
            </div>
        </div>
        <div class="bbox-buttons">

            <button type="button" class="custom-button" @click="generate_post"
                style="grid-column:1/2;grid-column: 1/2;">
                Generate
            </button>
            <button type="button" class="custom-button" @click="interrupt_this_inference"
                style="grid-column:1/2;grid-column: 2/3;">
                Interrupt
            </button>
            <button type="button" class="custom-button" @click="clear_voice_output"
                style="grid-column:1/2;grid-column: 3/4;">
                Clear Voice Output
            </button>
        </div>
        <hr>
        <div id="select-box">

            <div>
                gpt-weight select
            </div>
            <select name="gpt-weight" id="gpt-weight" v-model="gpt_selected">
                <option value="" selected>Default---{{ path_basename(default_gpt_weight) }}</option>
                <option :value="item" v-for="(item, index) in raw_candidate_weights['gpt_weights']">
                    {{ path_basename(item) }}</option>
            </select>

            <div>
                sovits-weight select
            </div>
            <select name="sovits-weight" id="sovits-weight" v-model="sovits_selected">
                <option value="" selected>Default---{{ path_basename(default_sovits_weight) }}</option>
                <option :value="item" v-for="(item, index) in raw_candidate_weights['sovits_weights']">{{
                path_basename(item) }}</option>
            </select>

            <div>
                language used to infer
            </div>
            <select name="language-select" id="language-select" v-model="language_selected">
                <option value="" selected>Default--- {{ path_basename(default_infer_language) }}</option>
                <option :value="item" v-for="(item, index) in languange_candidates">{{ item }}</option>
            </select>

            <div>
                relative speed
            </div>
            <!-- <button type="button" @click="()=>{relative_speed-=0.1;relative_speed=Number(relative_speed).toFixed(2)}"><</button> -->
            <input type="number" v-model="relative_speed" step="0.1" />
            <!-- <button type="button" @click="()=>{relative_speed+=0.1;relative_speed=Number(relative_speed).toFixed(2)}">></button> -->

        </div>



        <div id="voice-controls-textlist-container">

            <ul>
                <li v-for="page in filtered_text" :key="page.page_no" :id="generate_page_id(page.page_no)"
                    class="page_elem">
                    <p>
                        Page: {{ page.page_no }}
                    </p>
                    <ul>
                        <li v-for="block in page.blocks" :key="block.block_num"
                            :id="generate_block_id(page.page_no, block.block_num)" class="block_elem">
                            <p>
                                Block: {{ block.block_num }}: {{ block.text.length < shown_text_length ? block.text :
                block.text.slice(0, shown_text_length) + '...' }} </p>
                        </li>
                    </ul>
                </li>
            </ul>
        </div>

        <!-- <button @click="stopListening">Stop Listening</button> -->
    </div>
</template>


<style scoped>
.page_chosen {
    background-color: blanchedalmond;
}

.invisible {
    display: none;
}

ul {
    margin: 0;
    padding: 0;
}

li {
    margin-bottom: 3px;
    padding-left: 10px;
    list-style-type: none;
}

p {
    margin: 0;
    padding: 0;
}

#voice-minlength-container {
    display: flex;
    align-items: center;
    /* 垂直居中对齐 */
    justify-content: center;
}

.bbox-buttons {
    display: grid;
    grid-template-columns: (3, 1fr);
    grid-template-rows: (1, 1fr);
}

.bbox-buttons button {
    padding: 5px;
}

#select-box {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 1fr 1fr 1fr 1fr;
    grid-auto-flow: row;
}

.flex-container {
    display: flex;
    align-items: center;
    /* 垂直居中 */
}

.custom-button {
    padding: 5px;
    margin: 3px;
    font-size: 12px;
    border: 2px solid #ccc;
    border-radius: 5px;
    outline: none;
    transition: border-color 0.3s ease;

}
</style>