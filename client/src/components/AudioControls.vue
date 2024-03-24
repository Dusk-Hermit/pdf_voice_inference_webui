<script>
import axios from 'axios';
export default {
    data() {
        return {
            current_task_list: null,
            last_task_list: null,

            audio_list: [],

            message_to_display: '',
            main_loop_identifier: null,
        }
    },
    methods: {
        async get_task_list() {
            const path = this.BACKENDPATH+'/task_list';

            return axios.get(path)
                .then((response) => {
                    // console.log(response.data);
                    return response.data;
                })
                .catch((error) => {
                    console.log(error);
                })
        },
        async sleep(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        },
        async audio_load_main_loop() {
            // 伪代码：
            // 持续访问task_list，可以查看当前task所应该生成的音频地址list，以及已经存在的音频地址list
            // 把已经生成的音频地址list，加载到audio-container中，然后用一个变量list记录
            // 每次访问task_list时，如果inferencing是false，则只把此次访问获得的已存在音频地址list加载到audio-container中
            // 如果inferencing是true，则把新的音频地址，则加载到audio-container中
            // 另外：
            // 1、message_to_display显示当前task_list中的task内容
            // 2、已加载的audio的div的颜色，应该把本次task中的音频，和已存在的但是不在本次task中的音频区分开

            // 数据结构使用
            // 应该是一个列表，里面有多个obj，每个obj有地址+div索引
            const main_loop_identifier = Date.now();
            this.main_loop_identifier = main_loop_identifier

            this.clear_all();
            this.current_task_list = await this.get_task_list();
            this.renew_audio_list();

            if (!this.current_task_list['inferencing']) {
                console.log('inferencing is false, no need to load new audio');
                return;
            }

            while (true) {
                await this.sleep(1000 * 5);
                if (this.main_loop_identifier !== main_loop_identifier) {
                    console.log('main loop Interrupted.');
                    return;
                }

                const task_list = await this.get_task_list();
                if (task_list === this.last_task_list) {
                    continue;
                }
                this.last_task_list = this.current_task_list;
                this.current_task_list = task_list;

                this.renew_audio_list();


                if (!task_list['inferencing']) {
                    console.log('inferencing end.');
                    break;
                }

            }
            console.log('audio load end.');
        },
        renew_audio_list() {
            // 筛选出本次更新得到的新文件链接
            let temp_list = [];   // path列表，存放本次更新得到的新文件链接
            for (let i = 0; i < this.current_task_list['audio_already_exist'].length; i++) {
                temp_list.push(this.current_task_list['audio_already_exist'][i]);
                for (let j = 0; j < this.audio_list.length; j++) {
                    if (this.current_task_list['audio_already_exist'][i] === this.audio_list[j]['audio_path']) {
                        temp_list.pop();
                    }
                }
            }
            // console.log('new audio list:', temp_list);
            // console.log('current audio list:', this.current_task_list['audio_already_exist']);
            let audio_container = window.parent.document.getElementById('audio-container');

            // 对每个新文件链接，创建div
            for (let i = 0; i < temp_list.length; i++) {
                let index = 0;
                for (; index < this.audio_list.length; index++) {
                    if (temp_list[i] < this.audio_list[index]['audio_path']) {
                        break;
                    }
                }
                let audio_div = this.create_audio_div(temp_list[i]);
                if (index === this.audio_list.length) {
                    this.audio_list.push({ 'audio_path': temp_list[i], 'div': audio_div });
                    audio_container.appendChild(audio_div);
                } else {
                    this.audio_list.splice(index, 0, { 'audio_path': temp_list[i], 'div': audio_div });
                    audio_container.insertBefore(audio_div, audio_container.childNodes[index]);
                }

                // 设置样式
                if (this.current_task_list['task_outputs'].includes(temp_list[i])) {
                    audio_div.classList.add('current_task');
                }
                else {
                    audio_div.classList.remove('current_task');
                }
            }

        },
        create_audio_div(audio_path) {
            let audio_basename = audio_path.replaceAll('\\', '/').split('/').pop();

            let audio_warper=document.createElement('div')
            audio_warper.classList.add('audio-warper')

            let audio_div = document.createElement('audio');
            audio_div.controls = true
            audio_div.classList.add('audio_elem')

            let sourceElement = document.createElement('source');
            sourceElement.src = this.BACKENDPATH+'/audio/'+audio_basename;
            sourceElement.type = "audio/wav";
            audio_div.addEventListener('ended', () => {
                this.play_next_audio(audio_warper);
            });

            let description = document.createElement('p');
            description.textContent = audio_basename
            
            audio_warper.appendChild(description)
            audio_warper.appendChild(audio_div)
            audio_div.appendChild(sourceElement);

            return audio_warper;
        },
        clear_all(){
            for (let i = 0; i < this.audio_list.length; i++) {
                this.audio_list[i]['div'].remove();
            }
            this.audio_list = [];
            this.last_task_list = null;
            this.current_task_list = null;
        },
        async play_next_audio(audio_elem){
            const nextSilbling=audio_elem.nextElementSibling;
            const next_audio_elem=Array.from(nextSilbling.children).filter(elem=>elem.tagName==='AUDIO')[0];
            if (next_audio_elem&&next_audio_elem.tagName==='AUDIO'){
                await this.sleep(1000);
                next_audio_elem.play();
            }
        }

    },
    mounted() {

    },

}

</script>


<template>
    <div class="button-container">
        <button class="custom-button" @click="audio_load_main_loop">开始追踪task进度，持续加载已生成音频</button>

    </div>

    <div class="display-container">
        <p>{{ message_to_display }}</p>
    </div>

    <div class="audio-container" id="audio-container">


    </div>

</template>

<style scoped>
.current_task {
    background-color: beige;
}

.custom-button{
    padding: 5px;
    margin: 3px;
    font-size: 12px;
    border: 2px solid #ccc;
    border-radius: 5px;
    outline: none;
    transition: border-color 0.3s ease;

}
.button-container{
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 10px;
}
.audio-container{
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    /* margin-top: 10px; */
    padding: 10px
}
.audio_elem{
    height: 250px;
}
</style>