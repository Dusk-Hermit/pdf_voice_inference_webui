### 使用方法

#### 1
在 https://github.com/RVC-Boss/GPT-SoVITS 这个仓库下载GPT-SoVITS项目（windows版在这里有整合包），并使用它自带的webui，用你自己的音频素材，完成模型的训练
推荐教程：https://www.bilibili.com/video/BV1P541117yn/

*若不使用整合包，自己配置环境，应该修改`server/app.py`中`Popen`函数对应的调用的GPTSoVITS的python环境*

#### 2

克隆本项目，在合适的文件夹下，打开cmd执行：
```cmd
git clone https://github.com/Dusk-Hermit/pdf_voice_inference_webui.git
```

#### 3

使用conda虚拟环境，创建新环境，并安装依赖
*如果不是使用该名称的conda虚拟环境，则需要修改`run.py`的对应地方*
```
conda create -n pdf_voice_webui python=3.10
conda activate pdf_voice_webui
pip install -r requirements.txt
```

#### 4

用cmd进入`client`文件夹，并`npm install`。需要在机器上安装好nodejs
```cmd
cd client
npm install
```

#### 5
在`server/write_config.py`中，修改其中的`config_list`变量，并用任意python解释器执行以下该脚本`python write_config.py`，以更新`server/config.json`
需要修改的包括
- GPT_SoVITS项目的根目录地址
- 默认选择用来进行推理的GPT和SoVITS权重
- 作为当次推理的参考音频，应在3-10s内；以及它的对应文本和语言
- 默认打开的pdf文件目录（如果这是无效地址会启动失败……）
- *其他选项是可以不用特殊指定，有默认值的*

#### 6
在你的GPT_SoVITS项目根目录中，进入`GPT_SoVITS`文件夹，复制`inference_webui.py`一份，重命名为`inference_webui_copy.py`，*该名称在本项目中被引用，不应乱改*，然后这样修改`inference_webui_copy.py`：

1. 找到文件中的以下代码，并把这两行注释掉（这两行行首加上`#`）。*本项目通过对参考音频做音频时间处理，来实现推理语速控制*
```py
if (wav16k.shape[0] > 160000 or wav16k.shape[0] < 48000):
    raise OSError(i18n("参考音频在3~10秒范围外，请更换！"))
```
2. 从最后看，找到`with gr.Blocks(title="GPT-SoVITS WebUI") as app:`这一行，把这一行及以下所有代码删掉。*不同版本的GPT_SoVITS项目的该文件代码会有些许差别，因此请用自己下载的版本的该文件，并进行修改*

#### 6
双击`run.bat`即可打开webui



### 致谢
https://github.com/RVC-Boss/GPT-SoVITS