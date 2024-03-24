

## 开发小笔记

很多这些前后端开发的bug，遇到的是：
- 前端代码忘写了let const，vscode没有提示的……
- 对象的属性名访问错了，记错属性名，常见报错是访问一个undefined对象，undefined是在访问一个对象的不存在的属性时返回的
- 后端开发没有开dev版，使得有时候改了后端代码但是没重启，前端访问依旧看到有错误，抓耳挠腮了

对推理接口进行debug，可以对`server/app.py`中下面两行代码中的后面两行注释掉，来在控制台看这个进程的输出内容

```py
    global_config.p = subprocess.Popen(
        [os.path.join(GPTSOVITS_BASE,'runtime','python'),'inference_api.py'],
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
```