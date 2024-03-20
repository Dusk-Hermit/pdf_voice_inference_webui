from flask import Flask, Blueprint, send_file

app = Flask(__name__)

# 定义一个蓝图
wav_blueprint = Blueprint('wav', __name__)

# 定义模板方法来注册多个路由
def register_wav_routes(wav_blueprint, wav_file_paths):
    for i, wav_file_path in enumerate(wav_file_paths, start=1):
        # 定义每个路由处理函数
        @wav_blueprint.route(f'/get_wav{i}')
        def get_wav():
            return send_file(wav_file_path, mimetype='audio/wav')

# 定义多个 WAV 文件路径
wav_file_paths = ['path_to_your_wav_file_1.wav', 'path_to_your_wav_file_2.wav', ...]

# 注册蓝图并添加路由
register_wav_routes(wav_blueprint, wav_file_paths)
app.register_blueprint(wav_blueprint)

if __name__ == '__main__':
    app.run(debug=True)
