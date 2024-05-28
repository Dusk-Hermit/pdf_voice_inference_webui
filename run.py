import subprocess
import os
import signal
import time
import webbrowser
import json

def start_processes():
    # 开启第一个进程，执行 Flask 应用
    flask_process = subprocess.Popen(['cd','server','&','activate', 'pdf_voice_webui', '&', 'python', 'app.py'], shell=True)
    print("Flask process PID:", flask_process.pid)

    # 开启第二个进程，执行 npm run dev
    npm_process = subprocess.Popen(['cd','client','&','npm', 'run', 'dev'], shell=True)
    print("npm process PID:", npm_process.pid)

    return flask_process, npm_process

def stop_processes(processes):
    for process in processes:
        os.kill(process.pid, signal.SIGTERM)
    print("Processes terminated.")

if __name__ == "__main__":
    try:
        # 开启两个进程
        processes = start_processes()
        
        with open('server/config.json', 'r',encoding='utf-8') as f:
            config = json.loads(f.read())
            # 打开浏览器，访问client端口
            webbrowser.open(f'http://localhost:{config["client_port"]}')

        # 循环等待脚本停止
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # 如果脚本被停止，则终止两个进程
        stop_processes(processes)
