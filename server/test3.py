# 解决方法：使用蓝图注册多个路由

from flask import Flask, Blueprint, send_file, jsonify

app = Flask(__name__)

# 定义一个蓝图
wav_blueprint = Blueprint('wav', __name__)

# 定义模板方法来注册多个路由
def register_wav_routes(wav_blueprint, wav_file_paths):
    for i, wav_file_path in enumerate(wav_file_paths, start=1):
        # 定义每个路由处理函数
        def get_wav_func(wav_file_path=wav_file_path):
            return jsonify({'path': wav_file_path})
        
        # 为每个路由注册函数，并指定唯一的端点名
        wav_blueprint.add_url_rule(
            f'/get_wav{i}',
            endpoint=f'get_wav{i}',
            view_func=get_wav_func,
            methods=['GET']
        )

# 定义多个 WAV 文件路径
wav_file_paths = ['path_to_your_wav_file_1.wav', 'path_to_your_wav_file_2.wav']

# 注册蓝图并添加路由
register_wav_routes(wav_blueprint, wav_file_paths)
app.register_blueprint(wav_blueprint)

if __name__ == '__main__':
    app.run(debug=True)
