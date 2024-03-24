<script>
import VoiceControls from './VoiceControls.vue'
import AudioControls from './AudioControls.vue'
import axios from 'axios';
export default {
    data() {
        return {
            msg: 'hello',
            drawn: false,
            pdf_path: '',
            // Data fetched from backend
            size_and_font: {},
            bboxes: [],

            // Data preserving status; Already Sorted by string_length 
            size_font_data: [],
            counter: 5,
            bbox_on: false,
            // bbox_inited: false,
            virtual_div: document.createElement('div'),

            nav_num: 1,
            width_control: 0.3,
        }
    },
    components: {
        VoiceControls,
        AudioControls,
    },

    mounted() {
        Promise.all(
            [this.get_size_and_font(), this.get_bboxes()]
        ).then(
            () => {
                this.init_bboxes()
            }
        ).then(
            () => {
                this.update_data_by_counter()
                this.refresh_checkbox_by_data()
                this.bbox_respond_to_change()
                this.nav_bar_change(this.nav_num)
                this.change_width()
            }
        )

    },
    methods: {
        // Tools
        query_index_fun(list, font, size) {
            for (let i = 0; i < list.length; i++) {
                // console.log('compare:',font,size,list[i].font,list[i].size)
                if (list[i].font == font && list[i].size == size) return i
            }
            return -1

        },
        query_func(list, font, size, attr_str) {
            // console.log('list',list,'font',font,'size',size,'attr_str',attr_str)

            return list.filter(item => item.font == font && item.size == size)[0][attr_str]
        },
        make_id(font, size) {
            return font + '_' + size
        },

        // Get page contents and basic data
        get_size_and_font() {
            const path = this.BACKENDPATH + '/get_size_and_font'

            return new Promise((resolve, reject) =>
                axios.get(path).then(
                    (res) => {
                        // Get the size and font data: list and recommend
                        // list is the done thing convenient to render
                        // make res.data.recommend the main data structure saving status

                        this.size_and_font = res.data['list']
                        this.size_font_data = res.data['recommend']

                        // Sorting the list
                        this.size_and_font = this.size_and_font.sort(
                            (a, b) => Math.max.apply(null, a.size.map(item => this.query_func(this.size_font_data, a.font, item, 'string_length'))) - Math.max.apply(null, b.size.map(item => this.query_func(this.size_font_data, b.font, item, 'string_length')))
                        ).reverse()
                        this.size_and_font = this.size_and_font.map(item => {
                            return {
                                'font': item.font,
                                'size': item.size.sort(
                                    (a, b) => this.query_func(this.size_font_data, item.font, a, 'string_length') - this.query_func(this.size_font_data, item.font, b, 'string_length')
                                ).reverse()
                            };
                        })

                        // Init the size_font_data
                        this.size_font_data = this.size_font_data.map(
                            (item) => {
                                return {
                                    ...item,
                                    'chosen': false,
                                    'bbox_nodes': [],
                                }
                            }
                        )
                        // console.log('init size_font_data', this.size_font_data)
                        resolve()
                    }
                ).catch(
                    (error) => { console.log(error); reject(error) }
                )
            )
        },
        get_bboxes() {
            const path = this.BACKENDPATH + "/get_bboxes"
            return new Promise((resolve, reject) =>
                axios.get(path).then(
                    (res) => {
                        // console.log(res)
                        if (typeof (res.data) == 'string') {
                            this.bboxes = JSON.parse(res.data)
                        } else {

                            this.bboxes = res.data
                        }
                        // console.log(this.bboxes, typeof (this.bboxes))
                        // console.log('get_bboxes called')
                        resolve()
                    }
                ).catch(
                    (err) => { console.log(err); reject(err) }
                ))
        },

        // Post methods
        post_chosen_font_size() {
            const path = this.BACKENDPATH + "/post_font_size"
            const post_obj = this.size_font_data.filter((item) => item.chosen).map(item => { return { 'size': item.size, 'font': item.font, } })
            axios.post(path, post_obj)
                .then(
                    (res) => {
                        console.log(res)
                    }
                )
                .catch(
                    (err) => console.log(err)
                )

        },

        // Init bboxes
        init_bboxes() {
            const iframe = window.parent.document.getElementById('pdf-iframe')
            for (let i = 0; i < this.bboxes.length; i++) {
                let temp = this.bboxes[i]
                let element = this.create_one_bbox(temp.bbox, temp.page_size, temp.page_no, 'rgba(255,255,0,0.1)', iframe)
                let index = this.query_index_fun(this.size_font_data, temp.font, temp.size)

                // console.log('size_font_data',this.size_font_data)
                // console.log('index',index)
                // console.log(temp.font,temp.size,'temp')

                this.size_font_data[index].bbox_nodes.push({
                    'div': element,
                    'page_no': temp.page_no,
                })
            }
        },
        create_one_bbox(bbox_list, page_size_list, page_no, color, iframe) {
            const [x1, y1, x2, y2] = bbox_list
            const [width, height] = page_size_list

            // CSS
            const div = document.createElement('div')
            div.style.position = 'absolute'
            div.style.width = String(((x2 - x1) / width * 100).toFixed(2)) + '%'
            div.style.height = String(((y2 - y1) / height * 100).toFixed(2)) + '%'
            div.style.left = String((x1 / width * 100).toFixed(2)) + '%'
            div.style.top = String((y1 / height * 100).toFixed(2)) + '%'
            div.style.zIndex = '1'
            div.style.backgroundColor = color

            // Initial visibility is none
            div.classList.add('invisible')

            // DOM
            // console.log('iframe is:', iframe)
            // const pageList = window.parent.document.getElementById('pdf-iframe').contentWindow.document.querySelectorAll(`[data-page-number="${page_no}"]`)
            // console.log('pagelist:', pageList)
            // pageList[1].appendChild(div)

            return div
        },

        // Frontend logic
        // pdfs
        change_pdf() {
            if (this.pdf_path == '') return

            // 刷新其他组件的数据
            // this.$refs.VoiceControls.refre
            // this.$refs.AudioControls.clear_all()

            const path = this.BACKENDPATH + '/change_pdf'
            axios.post(path, {
                'path': this.pdf_path,
            }).then(
                (res) => {
                    history.go(0)

                }
            ).catch(
                (error) => { console.log(error) }
            ).then(
                () => {
                    this.$refs.VoiceControls.get_filtered_text()
                }
            )
        },
        keyup_submit(event) {
            if (event.keyCode == 13) {
                this.change_pdf()
            }
        },

        // Data collecting
        update_data_by_counter() {
            for (let i = 0; i < this.size_font_data.length; i++) {
                if (i < this.counter) this.size_font_data[i].chosen = true
                else this.size_font_data[i].chosen = false
            }
        },
        refresh_checkbox_by_data() {
            let candidate_id_list = this.size_font_data.filter(item => item.chosen).map(item => this.make_id(item.font, item.size))
            let checkbox_list = document.getElementById('choose_list').getElementsByTagName('input')
            for (let i = 0; i < checkbox_list.length; i++) {
                if (candidate_id_list.includes(checkbox_list[i].id)) checkbox_list[i].checked = true
                else checkbox_list[i].checked = false
            }
        },



        // Variable handle function
        update_data_by_checkbox_click(font, size) {
            let index = this.query_index_fun(this.size_font_data, font, size)
            this.size_font_data[index].chosen = !this.size_font_data[index].chosen
            this.refresh_checkbox_by_data()
            this.bbox_respond_to_change()
        },
        bbox_respond_to_change() {
            if (this.bbox_on) {
                this.detach_all_bbox()
                this.attach_chosen_bbox()
            } else {
                this.detach_all_bbox()
            }
        },
        detach_all_bbox() {
            for (let i = 0; i < this.size_font_data.length; i++) {
                const bbox_nodes = this.size_font_data[i].bbox_nodes
                for (let j = 0; j < bbox_nodes.length; j++) {
                    this.virtual_div.appendChild(bbox_nodes[j].div)
                }
            }
        },
        attach_chosen_bbox() {
            const iframe = window.parent.document.getElementById('pdf-iframe')
            for (let i = 0; i < this.size_font_data.length; i++) {
                if (this.size_font_data[i].chosen) {
                    const bbox_nodes = this.size_font_data[i].bbox_nodes
                    for (let j = 0; j < bbox_nodes.length; j++) {
                        const pageList = iframe.contentWindow.document.querySelectorAll(`[data-page-number="${bbox_nodes[j].page_no}"]`)
                        pageList[1].appendChild(bbox_nodes[j].div)

                    }
                }
            }
        },

        // Botton logic
        bbox_on_change() {
            // if (!this.bbox_inited) this.attach_bboxes()

            this.bbox_on = !this.bbox_on

            if (this.bbox_on) {
                this.attach_chosen_bbox()
            } else {
                this.detach_all_bbox()
            }
            const iframe = window.parent.document.getElementById('pdf-iframe')
            // iframe.contentWindow.location.reload()

        },

        // Botton logic
        choose_all() {
            for (let i = 0; i < this.size_font_data.length; i++) {
                this.size_font_data[i].chosen = true
            }
            this.refresh_checkbox_by_data()
            this.bbox_respond_to_change()
        },
        choose_none() {
            for (let i = 0; i < this.size_font_data.length; i++) {
                this.size_font_data[i].chosen = false
            }
            this.refresh_checkbox_by_data()
            this.bbox_respond_to_change()
        },

        // Counter operations
        counter_increment() {
            if (this.counter == this.size_font_data.length) return
            this.counter++
            this.update_data_by_counter()
            this.refresh_checkbox_by_data()
            this.bbox_respond_to_change()
        },
        counter_decrement() {
            if (this.counter == 0) return
            this.counter--
            this.update_data_by_counter()
            this.refresh_checkbox_by_data()
            this.bbox_respond_to_change()
        },
        nav_bar_change(num) {
            if (this.nav_num == num) return
            this.nav_num = num

            this.nav_bar_visibility_rerender(num)
            if (this.nav_num == 2) {
                this.post_chosen_font_size()
                this.$refs.VoiceControls.get_filtered_text()
                this.$refs.VoiceControls.page_select()
                this.change_width()
            }
        },
        nav_bar_visibility_rerender(num) {
            // nav button rerender
            const nav_header = window.parent.document.getElementById('nav-header')
            for (let i = 0; i < nav_header.children.length; i++) {
                if (i == num - 1) nav_header.children[i].classList.add('nav-button-active')
                else nav_header.children[i].classList.remove('nav-button-active')
            }


            // nav_num=true : bbox selecting bar
            const nav_1 = window.parent.document.getElementById('nav-1')
            const nav_2 = window.parent.document.getElementById('nav-2')
            const nav_3 = window.parent.document.getElementById('nav-3')
            let nav_list = [nav_1, nav_2, nav_3]
            for (let i = 1; i <= nav_list.length; i++) {
                // if (nav_list[i]==undefined) console.log('nav_list[',i,'] is undefined')

                if (i == num) nav_list[i - 1].classList.remove('invisible')
                else nav_list[i - 1].classList.add('invisible')
            }
        },
        reload_config() {
            const path = this.BACKENDPATH + '/reload_config'
            axios.post(path, {}).then(
                (res) => {
                    console.log(res)
                }
            ).catch(
                (error) => { console.log(error) }
            )
        },
        change_width() {
            if (this.width_control < 0.15) this.width_control = 0.15
            if (this.width_control > 0.8) this.width_control = 0.8

            const left_width = String(this.width_control * 100) + '%'
            const right_width = String((1 - this.width_control) * 100) + '%'
            const left = window.parent.document.getElementById('left')
            const right = window.parent.document.getElementById('right')
            left.style.width = left_width
            right.style.width = right_width

            let absolute_width = window.parent.document.getElementById('left').offsetWidth - 50
            absolute_width = absolute_width > 0 ? absolute_width : 0
            this.$refs.VoiceControls.shown_text_length = Math.floor(absolute_width / 10)

            // logo height change
            const logo = window.parent.document.getElementsByClassName('background-image')[0]
            logo.style.height=Math.floor(logo.offsetWidth*0.75)+'px'
            // logo.style.height=logo.offsetWidth*0.75+'px'
        }
    }

}


</script>

<template>
    <div class="controls-container">
        <div class="background-image">

        </div>
        <div class="line-1">

            <!-- <div class="width-control"> -->
            <div style="background-color: white;grid-row:1/2;grid-column: 1/2;border: 2px solid #ccc;    border-radius: 5px;width: 80%;text-align: center;padding: 5px;margin: 5px;">

                左侧栏宽度比例：
            </div>
            <input type="number" step="0.05" max="0.8" min="0.15" v-model="width_control" @input="change_width"
                class="custom-input" style="grid-row:1/2;grid-column: 2/3;" />
            <!-- </div>
            <div class="pdf-changer"> -->
            <input type="text" placeholder="请输入pdf路径" v-model="pdf_path" @keyup="keyup_submit"
                style="width:90%;grid-row:2/3;grid-column: 1/2;" />
            <button type="button" class="custom-button" @click="change_pdf" style="grid-row:2/3;grid-column: 2/3;">
                确认切换
            </button>
            <!-- </div> -->
        </div>
        <hr>

        <div class="nav-header" id="nav-header">
            <button type="button" class="btn btn-sm nav-button-active" @click="() => nav_bar_change(1)">
                视图 1
            </button>
            <button type="button" class="btn btn-sm" @click="() => nav_bar_change(2)">
                视图 2
            </button>
            <button type="button" class="btn btn-sm" @click="() => nav_bar_change(3)">
                视图 3
            </button>
        </div>
        <hr>

        <div class="bbox-buttons">


            <button type="button" class="custom-button" @click="bbox_on_change" style="grid-row:1/2;grid-column: 1/3;">
                {{ bbox_on ? "点击隐藏Bounding Box" : "点击显示Bounding Box" }}
            </button>

            <button type="button" class="custom-button" @click="bbox_respond_to_change"
                style="grid-row:2/3;grid-column: 1/3;">
                Refresh Bbox
            </button>

            <button type="button" class="custom-button" @click="choose_all" style="grid-row:3/4;grid-column: 1/2;">
                Choose All
            </button>
            <button type="button" class="custom-button" @click="choose_none" style="grid-row:3/4;grid-column: 2/3;">
                Choose None
            </button>

            <!-- <button type="button" class="custom-button" @click="post_chosen_font_size">
                Generate Voice!
            </button> -->
            <button type="button" class="custom-button" @click="reload_config" style="grid-row:4/5;grid-column: 1/3;">
                config.json Reload
            </button>

        </div>
        <hr>

        <div class="nav-1" id="nav-1">


            <div class="counter-container">
                <p>按照pdf中字体对应的文字数量，</p>
                <p>选择前n种字体</p>
                <div class="input-group">

                    <button class="btn" type="button" @click="counter_decrement">-</button>

                    <input type="text" class="text-center custom-input" v-model="counter" readonly>

                    <button class="btn" type="button" @click="counter_increment">+</button>

                </div>
            </div>


            <!-- <div>{{ size_and_font }}</div> -->
            <hr>
            <div class="list-container">
                <ul class="list-group" id="choose_list">
                    <li class="list-group-item" v-for="(elem, key) in size_and_font" :key="key">
                        {{ elem.font }}
                        <ul>
                            <li v-for="(size_elem, index) in elem.size" :key="index">
                                <label>
                                    <input type="checkbox" :id="elem.font + '_' + size_elem"
                                        @click="update_data_by_checkbox_click(elem.font, size_elem)"></input>
                                    {{ size_elem }}(chars:
                                    {{ query_func(size_font_data, elem.font, size_elem, 'string_length') }})
                                </label>
                            </li>
                        </ul>
                    </li>
                </ul>

            </div>
        </div>
        <div class="nav-2 invisible" id="nav-2">
            <VoiceControls ref="VoiceControls" />
        </div>
        <div class="nav-3 invisible" id="nav-3">
            <AudioControls />
        </div>
    </div>

</template>

<style scoped>
.logo-img {
    text-align: center;
    margin-top: 10px;
    width: 100px;
}

.controls-container {
    width: 100%;
    height: 100%;
}

.hide_all_bbox {
    visibility: hidden;
}

.invisible {
    display: none;
}

.nav-1 {
    height: 100%;
    overflow-y: hidden;
}

.nav-header {
    background-color: #f5f5f5;
    padding: 5px;
    box-shadow: 5px 5px 5px #00000033;
    display: flex;
}

.nav-header button {
    position: relative;
    flex: 1;
    margin: 2px;
    font: 500 20px '优设标题黑';
}

.nav-header button:hover {
    color: #00000062;
}

.nav-button-active {
    background-color: rgb(196, 214, 214);
}

.list-container {
    height: 100%;
    /* overflow-y: auto; */
}

.width-control {
    display: flex;
    align-items: center;
}

.pdf-changer {
    display: flex;
    align-items: center;

}

.controls-container input[type='text'] {
    width: 45%;
    padding: 5px;
    margin: 5px;
    font-size: 12px;
    border: 2px solid #ccc;
    border-radius: 5px;
    outline: none;
    transition: border-color 0.3s ease;
}

.controls-container input[type='number'] {
    width: 30%;
    padding: 5px;
    margin: 5px;
    font-size: 12px;
    border: 2px solid #ccc;
    border-radius: 5px;
    outline: none;
    transition: border-color 0.3s ease;
}

.input-group {
    /* position: relative; */
    display: flex;
    /* align-items: center; */
    justify-content: center;
}

.counter-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;

}

p {
    margin: 0;
    padding: 0;
}

/* .counter-container p{
    margin: 5px;
} */
.input-description {
    width: 50%;
    padding: 5px;
    margin: 5px;
    font-size: 12px;
    /* border: 2px solid #ccc;
  border-radius: 5px; */
}

.custom-input:focus {
    border-color: #91cfd1;
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

.controls-container li {
    list-style-type: none;
}

.controls-container {
    font-size: small;
    font-family: PingFang SC, HarmonyOS_Regular, Helvetica Neue, Microsoft YaHei, sans-serif;
}

.bbox-buttons {
    display: grid;
    grid-template-columns: (2, 1fr);
    grid-template-rows: (4, 1fr);
}

.bbox-buttons button {
    padding: 5px;
}
.background-image{
    width: 100%;
    background-image: url('../assets/image/logo.png');
    background-size: 100% auto;
    background-color: rgba(255, 255, 255, 0.5);
    position: relative;

    background-position-x: center;
}
.line-1 {
    width: 100%;
    /* height: 285px; */
    /* background-position-y: -20px; */
    /* padding-top: 75%; */
    /* background-position: center; */
    /* box-sizing: border-box; */

    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 1fr 1fr ;
}
</style>