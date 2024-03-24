import json, os

config_list = {
    "GPTSOVITS_BASE": r"D:\git_download\GPT-SoVITS-beta0217",
    "default_gpt_weight":r"D:\git_download\GPT-SoVITS-beta0217\GPT_weights\saileach-e15.ckpt",
    "default_sovits_weight":r"D:\git_download\GPT-SoVITS-beta0217\SoVITS_weights\saileach_e8_s232.pth",
    # "output_base":r"D:\git_download\GPT-SoVITS-beta0217\pdf_inference_webui\output",
    
    "ref_wav_path":r"C:\Users\Dusk_Hermit\Desktop\saileach\raw\信赖触摸.wav",
    "prompt_text":"您是不是累了？这是我烤的甜司康饼。您可以坐下来，喝点茶，与我说说您的烦心事。",
    "prompt_language_text":"中文",
    
    # "default_infer_language":"中英混合",
    
    'default_pdf_path':r"D:\git_download\read-aloud\1706.03762.pdf",
}

with open(
    os.path.join(os.path.dirname(__file__), "config.json"), "w", encoding="utf-8"
) as f:
    f.write(json.dumps(config_list, ensure_ascii=False, indent=4))
