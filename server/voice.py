import numpy as np
import librosa
import soundfile as sf

def func(input_file,output_file,rate):
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
    threshold = 0.5  # 设定阈值
    mask = np.ones_like(stft)
    mask[:, np.max(np.abs(stft), axis=0) < threshold] = 0  # 根据阈值选择要保留的频率成分

    # 应用时间频率掩模
    masked_stft = stft * mask

    # 逆短时傅里叶变换（ISTFT）
    masked_y = librosa.istft(masked_stft, hop_length=hop_length)

    # 保存为新的wav文件
    sf.write(output_file, masked_y, sr)  

# # 读取原始wav文件
input_file = r"C:\Users\Dusk_Hermit\Desktop\saileach\raw\信赖触摸.wav"
output_file = 'slowed.wav'
func(input_file,output_file,0.5)