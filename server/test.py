import subprocess
import time
import io

# 启动子进程执行命令
p = subprocess.Popen(
    ["batch.bat"],
    # ["batch copy.bat"],
    # ['dir .'],
    shell=True,
    stdout=subprocess.DEVNULL,
    # stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    # stderr=subprocess.PIPE,
    # bufsize=1,
)
print(f"pid: {p.pid}")

# 设置标准输出为非阻塞模式
# stdout_reader = io.TextIOWrapper(io.BufferedReader(p.stdout), errors="ignore")

# 读取标准输出的数据
# output_data = ""
while True:
    print('waiting')
    time.sleep(1)
    
    if p.poll() is not None:
        print('break')
        stdout_data, stderr_data = p.communicate()
        print(stdout_data)
        break