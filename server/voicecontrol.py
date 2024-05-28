import os, json
import re
import numpy as np
import librosa
import soundfile as sf

language_text = [
    "中文",
    "英文",
    "日文",
    "中英混合",
    "日英混合",
    "多语种混合",
]


class VoiceControl:
    def __init__(self) -> None:
        self.renew_default_config()

        self.chosen_gpt_weight=''
        self.chosen_sovits_weight=''
        self.infer_language=''
        
        self.relative_speed=1.0

    def get_gpt_weight_choices(self):
        return [
            os.path.join(self.gpt_weight_dir, k)
            for k in os.listdir(self.gpt_weight_dir)
        ]

    def get_sovits_weight_choices(self):
        return [
            os.path.join(self.sovits_weight_dir, k)
            for k in os.listdir(self.sovits_weight_dir)
        ]

    def return_chosen_gpt_weight(self):
        if self.chosen_gpt_weight:
            return self.chosen_gpt_weight
        else:
            return self.default_gpt_weight
    
    def return_chosen_sovits_weight(self):
        if self.chosen_sovits_weight:
            return self.chosen_sovits_weight
        else:
            return self.default_sovits_weight
    
    def return_infer_language(self):
        if self.infer_language:
            return self.infer_language
        else:
            return self.default_infer_language
    
    def renew_default_config(self):
        with open(
            os.path.join(os.path.dirname(__file__), "config.json"),
            "r",
            encoding="utf-8",
        ) as f:
            config = json.load(f)

        self.gptsovits_base = config["GPTSOVITS_BASE"]
        self.default_gpt_weight = config["default_gpt_weight"] if "default_gpt_weight" in config else os.path.join(self.gptsovits_base, r"GPT_SoVITS/pretrained_models/s1bert25hz-2kh-longer-epoch=68e-step=50232.ckpt")
        self.default_sovits_weight = config["default_sovits_weight"]if "default_sovits_weight" in config else os.path.join(self.gptsovits_base, r"GPT_SoVITS/pretrained_models/s2G488k.pth")
        self.ref_wav_path = config["ref_wav_path"]if "ref_wav_path" in config else ''
        self.prompt_text = config["prompt_text"]if "prompt_text" in config else ''
        self.prompt_language_text = config["prompt_language_text"]if "prompt_language_text" in config else ''
        self.output_base = config["output_base"] if "output_base" in config else os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
        self.default_infer_language = config["default_infer_language"] if "default_infer_language" in config else "中英混合"

        self.gpt_weight_dir = os.path.join(self.gptsovits_base, "GPT_weights")
        self.sovits_weight_dir = os.path.join(self.gptsovits_base, "SoVITS_weights")
        
        print(f"self.default_gpt_weight: {self.default_gpt_weight}")
        print(f"self.default_sovits_weight: {self.default_sovits_weight}")
        print(f"self.ref_wav_path: {self.ref_wav_path}")
        print(f"self.prompt_text: {self.prompt_text}")
        print(f"self.prompt_language_text: {self.prompt_language_text}")
        print(f"self.output_base: {self.output_base}")
        print(f"self.default_infer_language: {self.default_infer_language}")
        print(f"self.gpt_weight_dir: {self.gpt_weight_dir}")
        print(f"self.sovits_weight_dir: {self.sovits_weight_dir}")
        
    
    def text_process(self,text):
        text=self.text_clean(text)
        
        text_list=text.replace('- ','').replace(', ','\n').replace('. ','\n').replace('，','\n').replace('。','\n').replace('！','!').replace('!','\n').replace('？','?').replace('?','\n').replace('  ',' ').split('\n')
        text_list=[k.strip() for k in text_list if k]
        print(text_list)
        # 50字一段，总是以句号结尾
        text_list_new=[]
        temp=''
        for k in text_list:
            if len(temp)<50:
                temp+=k+'.'
            else:
                text_list_new.append(temp)
                temp=k+'.'
        if len(text_list_new)==0:
            text_list_new.append(temp)
        else:
            text_list_new[-1]+=temp
        
        text='\n'.join(text_list_new)        
        
        return text
    
    def text_clean(self,text):
        text=re.sub(r'\[[0-9,\s]*?\]',' ',text)
        return text
    
    def wav_speed_change(self,input_file,output_file,rate,threshold=0.5):
        # feat chatgpt
        y, sr = librosa.load(input_file, sr=None)
        
        # 将音频放慢0.5倍速度
        y_slow = librosa.effects.time_stretch(y, rate=rate)

        # 重新采样为原音频的频率
        y_resampled = librosa.resample(y_slow, orig_sr=sr, target_sr=sr)

        # 计算短时傅里叶变换（STFT）
        n_fft = 2048
        hop_length = 512
        stft = librosa.stft(y_resampled, n_fft=n_fft, hop_length=hop_length)

        # 创建时间频率掩模
        mask = np.ones_like(stft)
        mask[:, np.max(np.abs(stft), axis=0) < threshold] = 0  # 根据阈值选择要保留的频率成分

        # 应用时间频率掩模
        masked_stft = stft * mask

        # 逆短时傅里叶变换（ISTFT）
        masked_y = librosa.istft(masked_stft, hop_length=hop_length)

        # 保存为新的wav文件
        sf.write(output_file, masked_y, sr)  

if __name__ == "__main__":
    vc=VoiceControl()
    # vc.wav_speed_change(r"D:\git_download\GPT-SoVITS-beta0217\pdf_inference_webui\server\slowed.wav",r"D:\git_download\GPT-SoVITS-beta0217\pdf_inference_webui\server\slowed2.wav",0.8)
    
    print(vc.text_process('''A central task in the application of probabilistic models is the evaluation of the pos-
terior distribution p(Z|X) of the latent variables Z given the observed (visible) data
variables X, and the evaluation of expectations computed with respect to this dis-
tribution. The model might also contain some deterministic parameters, which we
will leave implicit for the moment, or it may be a '''))