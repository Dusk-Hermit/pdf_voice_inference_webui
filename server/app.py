from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

from pdf import PDFObject
from voicecontrol import VoiceControl

import subprocess, json, os

with open('config.json','r',encoding='utf-8') as f:
    config=json.load(f)
GPTSOVITS_BASE=config['GPTSOVITS_BASE']

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)


class GlobalConfig:
    def __init__(self):
        self.pdf_file_path = self.get_default_pdf_path()
        self.pdf = PDFObject(self.pdf_file_path)

        self.size_font_filter = []
        self.page_max_no = len(self.pdf.pages)
        self.page_selected = [k + 1 for k in range(self.page_max_no)]
        self.minlength = 0

        self.voicecontrol = VoiceControl()

        self.should_interrupt = False
        self.inferencing = False
        
        self.server_port,self.client_port = self.get_port()

        self.p = None
    def get_default_pdf_path(self):
        with open(os.path.join(os.path.dirname(__file__), "config.json"), "r", encoding="utf-8") as f:
            config = json.load(f)
        return config["default_pdf_path"]
    def get_port(self):
        with open(os.path.join(os.path.dirname(__file__), "config.json"), "r", encoding="utf-8") as f:
            config = json.load(f)
        return config["server_port"],config['client_port']
    def write_default_pdf_path(self,pdf_path):
        with open(os.path.join(os.path.dirname(__file__), "config.json"), "r", encoding="utf-8") as f:
            config = json.load(f)
        config["default_pdf_path"]=pdf_path
        with open(os.path.join(os.path.dirname(__file__), "config.json"), "w", encoding="utf-8") as f:
            f.write(json.dumps(config, ensure_ascii=False, indent=4))

global_config = GlobalConfig()

# enable CORS
CORS(app, resources={r"/*": {"origins": f"http://localhost:{global_config.client_port}"}})



@app.route("/pdf", methods=["GET"])
def send_pdf():
    print(global_config.pdf_file_path)
    return send_file(
        global_config.pdf_file_path,
        mimetype="application/pdf",
        download_name="test.pdf",
    )


@app.route("/change_pdf", methods=["POST"])
def change_config():
    post_data = request.get_json()
    print(post_data)
    pdf_path = post_data["path"]

    for s in ['"', "'"]:
        pdf_path = pdf_path.replace(s, "")
    pdf_path = pdf_path.replace("\\", "/")

    global_config.pdf_file_path = pdf_path
    global_config.write_default_pdf_path(pdf_path)
    
    global_config.pdf = PDFObject(pdf_path)

    return jsonify("success")


@app.route("/get_size_and_font", methods=["GET"])
def get_size_and_font():
    print("get_size_and_font called")
    return jsonify(global_config.pdf.size_with_fonts())


@app.route("/get_bboxes", methods=["GET"])
def get_bboxes():
    print("get_bboxes called")
    return jsonify(global_config.pdf.get_bboxes())


@app.route("/post_font_size", methods=["POST"])
def start_generate():
    post_data = request.get_json()
    print(post_data)
    global_config.size_font_filter = post_data
    return jsonify("start_generate now!")


@app.route("/get_filtered_text", methods=["GET"])
def get_filtered_text():
    print(global_config.size_font_filter)
    return jsonify(
        {
            "text": global_config.pdf.get_merged_text_by_size_font(
                global_config.size_font_filter
            ).to_dict(orient="records"),
            "page_max_no": global_config.page_max_no,
            "default_infer_language": global_config.voicecontrol.default_infer_language,
            "default_gpt_weight": global_config.voicecontrol.default_gpt_weight,
            "default_sovits_weight": global_config.voicecontrol.default_sovits_weight,
        }
    )


@app.route("/generate_post", methods=["POST"])
def generate_handle():
    post_data = request.get_json()
    global_config.minlength = m = post_data["minlength"]
    global_config.page_selected = p = post_data["page_selected"]
    global_config.voicecontrol.chosen_gpt_weight = w1 = post_data["gpt_weight"]
    global_config.voicecontrol.chosen_sovits_weight = w2 = post_data["sovits_weight"]
    global_config.voicecontrol.infer_language = l = post_data["languange_selected"]
    global_config.voicecontrol.relative_speed = rs = post_data["relative_speed"]

    print(
        f"Started generating. minlength={m}, page_selected={p}, gpt-weight={w1}, sovits-weight={w2}, infer language={l}, relative speed={rs}"
    )

    # 写入data.json为本次task
    # df有这些筛选条件：minlength, page_selected,size,font
    df = global_config.pdf.get_merged_text_by_size_font(global_config.size_font_filter)
    df = df[df.apply(lambda x: x["page_no"] in p and len(x["text"]) >= m, axis=1)]
    df_list = df.to_dict(orient="records")
    df_dict = {"data": df_list}
    df_dict.update(
        post_data,
    )
    if_success = make_task_json(df_dict)
    if not if_success:
        return jsonify(
            {
                "message": "Please set ref_wav_path and prompt_text and prompt_language_text in config.json",
            }
        )

    # 调用popen，设置为self.p
    global_config.p = subprocess.Popen(
        [os.path.join(GPTSOVITS_BASE,'runtime','python'),'inference_api.py'],
        shell=True,
        # stdout=subprocess.DEVNULL,
        # stderr=subprocess.DEVNULL,
    )
    print(f"pid: {global_config.p.pid}")

    # 设置inferencing为True
    global_config.inferencing = True
    return jsonify(
        {
            "message": "Started generating",
        }
    )


def voice_output_path(page_no, block_num):
    pdf_name = get_this_pdf_name_for_dir()
    return os.path.join(
        global_config.voicecontrol.output_base,
        pdf_name,
        'voice_output',
        f"page_{str(page_no).zfill(4)}_block_{str(block_num).zfill(4)}.wav",
    )

def generate_temp_ref_wav_path():
    pdf_name = get_this_pdf_name_for_dir()
    return os.path.join(
        global_config.voicecontrol.output_base,
        pdf_name,
        "temp_ref.wav",
    )

def get_this_pdf_name():
    return ".".join(os.path.basename(global_config.pdf_file_path).split(".")[:-1])

def get_this_pdf_name_for_dir():
    return get_this_pdf_name().strip()

def make_task_json(params):
    # with open('tempdata.json','w',encoding='utf-8') as f:
    #     json.dump(params,f,ensure_ascii=False,indent=4)

    ref_wav_path = global_config.voicecontrol.ref_wav_path
    prompt_text = global_config.voicecontrol.prompt_text
    prompt_language_text = global_config.voicecontrol.prompt_language_text
    if ref_wav_path == "" or prompt_text == "" or prompt_language_text == "":
        # 需要自己配置好ref_wav_path和prompt_text和prompt_language_text在config.json中的值
        return False

    # 文件夹建立
    os.makedirs(os.path.join(global_config.voicecontrol.output_base, get_this_pdf_name_for_dir(), 'voice_output'), exist_ok=True)

    # 调整ref_wav的速率并保存为暂存文件
    temp_ref_wav_path = generate_temp_ref_wav_path()
    print(f"temp_ref_wav_path: {temp_ref_wav_path}, ref_wav_path: {ref_wav_path}, relative_speed: {global_config.voicecontrol.relative_speed}")
    global_config.voicecontrol.wav_speed_change(ref_wav_path, temp_ref_wav_path, global_config.voicecontrol.relative_speed)
    

    infer_language = global_config.voicecontrol.return_infer_language()

    processed_prompt_text = global_config.voicecontrol.text_process(prompt_text)

    lines_list = [
        {
            "ref_wav_path": temp_ref_wav_path,
            "prompt_text": processed_prompt_text,
            "prompt_language_text": prompt_language_text,
            "text": global_config.voicecontrol.text_process(k["text"]),
            "text_language_text": infer_language,
            "output_file_path": voice_output_path(k["page_no"], k["block_num"]),
        }
        for k in params["data"]
    ]

    task_data = [
        {
            "gpt_weight": global_config.voicecontrol.return_chosen_gpt_weight(),
            "sovits_weight": global_config.voicecontrol.return_chosen_sovits_weight(),
            "lines": lines_list,
        }
    ]
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(task_data, f, ensure_ascii=False, indent=4)
    return True


@app.route("/candidate_weights", methods=["GET"])
def candidate_weights():
    return jsonify(
        {
            "gpt_weights": global_config.voicecontrol.get_gpt_weight_choices(),
            "sovits_weights": global_config.voicecontrol.get_sovits_weight_choices(),
        }
    )


# 前端发来generate或者interrupt的请求
# 后端主进程就设置状态变量
# inferencing变量从false变true，只有前端generate请求
# inferencing变量从true变false，可以是生成完了，也可以是interrupt后接收到最后一次子进程的请求
# should_interrupt变量从false变true，只有前端interrupt请求，且只有inferencing变量为true时才行
# should_interrupt变量从true变false，是（最后一次）和子进程通信后的结果

# integrity：inferencing=false时，不应该有子进程在运行（即finished_one_inference只有在inferencing=true时被请求），且should_interrupt=false


@app.route("/set_interrupt", methods=["POST",'GET'])
def set_interrupt():
    """
    Frontend interrupt request
    """
    if global_config.inferencing:
        global_config.should_interrupt = True
    # 如果inference进程异常退出，已经结束，则设置inferencing为False
    if global_config.p.poll() is not None:
        global_config.inferencing = False
    return jsonify("interrupt set")


@app.route("/finished_one_inference", methods=["POST"])
def finished_one_inference():
    """
    Communicate with subprocess, which is the inference process
    """
    post_data = request.get_json()
    this_output = post_data["output_file_path"]
    if_end = post_data["if_end"]

    return_obj = {
        "should_interrupt": global_config.should_interrupt,
    }
    global_config.inferencing = not (if_end  or global_config.should_interrupt)
    if not global_config.inferencing:
        if global_config.should_interrupt:
            print("--------------Interrupting--------------")
        else:
            print("--------------Finished--------------")
    global_config.should_interrupt = False
    
    print(f"finished one inference: {this_output}, inferencing={global_config.inferencing}, should_interrupt={global_config.should_interrupt}")

    return jsonify(return_obj)

@app.route("/reload_config", methods=["POST"])
def reload_config():
    global_config.voicecontrol.renew_default_config()
    return jsonify("config reloaded")

@app.route("/clear_voice_output", methods=["POST",'GET'])
def clear_voice_output():

    pdf_name = get_this_pdf_name_for_dir()
    voice_output_dir = os.path.join(global_config.voicecontrol.output_base, pdf_name, 'voice_output')
    for f in os.listdir(voice_output_dir):
        os.remove(os.path.join(voice_output_dir, f))
    return jsonify("voice output cleared")

# @socketio.on('connect')
# def connect():
#     # print('connected with client')
#     emit('connect', {
#         'message': 'Connected to server',
#     })

@app.route("/task_list", methods=['GET'])
def task_list():
    this_output_path=os.path.join(global_config.voicecontrol.output_base,get_this_pdf_name_for_dir(),'voice_output')
    audio_already_exist=[os.path.join(this_output_path,f) for f in os.listdir(this_output_path)]
    if os.path.exists('data.json'):
        with open('data.json','r',encoding='utf-8') as f:
            obj=json.load(f)
            task_outputs=[k['output_file_path'] for task_item in obj for k in task_item['lines']]
        
        return jsonify({
            'task_outputs':task_outputs,
            'audio_already_exist':audio_already_exist,
            "inferencing":global_config.inferencing,
            'no_task':False,
        })
    else:
        return jsonify({
            'audio_already_exist':audio_already_exist,
            "inferencing":global_config.inferencing,
            'no_task':True,
        })
    

@app.route('/audio/<path:filename>')
def serve_audio(filename):
    # 返回 WAV 音频文件
    absolute_file_path= os.path.join(
        global_config.voicecontrol.output_base,
        get_this_pdf_name_for_dir(),
        'voice_output',
        filename
    )
    
    return send_file(absolute_file_path, mimetype='audio/wav')


    
if __name__ == "__main__":
    app.run(debug=False, port=global_config.server_port)
