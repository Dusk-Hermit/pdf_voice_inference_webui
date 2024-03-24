### 使用方法

#### 1
在 https://github.com/RVC-Boss/GPT-SoVITS 这个仓库下载GPT-SoVITS项目（windows版在这里有整合包），并使用它自带的webui，用你自己的音频素材，完成模型的训练
推荐教程：https://www.bilibili.com/video/BV1P541117yn/

*若不使用整合包，自己安装路径，应该修改`server/app.py`中`Popen`函数对应的调用的GPTSoVITS的python环境*

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
在`server/write_config.py`中，修改config_list并用任意python解释器执行以下该脚本，以更新`server/config.json`
需要修改的包括
- GPT_SoVITS项目的根目录地址
- 默认选择用来进行推理的GPT和SoVITS权重
- 作为当次推理的参考音频，应在3-10s内；以及它的对应文本和语言
- 默认打开的pdf文件目录（如果这是无效地址会启动失败……）
- *其他选项是可以不用特殊指定，有默认值的*

#### 5
复制`inference_webui_copy.py`文件，到你的GPT_SoVITS项目目录下的`GPT_SoVITS`文件夹中，该文件夹中应本有一个`inference_webui.py`文件。*这个copy文件实际上就是前者注释掉两行，然后再删掉启动它的webui的代码*

#### 6
双击`run.bat`即可打开