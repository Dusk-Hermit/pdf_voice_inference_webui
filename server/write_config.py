import json, os

config_list = {
    "GPTSOVITS_BASE": r"D:\repos\GPT-SoVITS-beta0306fix2",
    "default_gpt_weight":r"D:\repos\GPT-SoVITS-beta0306fix2\GPT_weights\auto_花火2_huahuo-e100.ckpt",
    "default_sovits_weight":r"D:\repos\GPT-SoVITS-beta0306fix2\SoVITS_weights\auto_花火2_huahuo_e100_s1100.pth",
    # "output_base":r"D:\git_download\GPT-SoVITS-beta0217\pdf_inference_webui\output",
    
    "ref_wav_path":r"E:\GPTsoVITs权重\花火2\refer_audio\好吧好吧～我只是想说…如果你需要，我随时都可以帮你哦？谁能拒绝一位在鸡翅膀上打钉饰的男孩呢？.wav",
    "prompt_text":"好吧好吧～我只是想说…如果你需要，我随时都可以帮你哦？谁能拒绝一位在鸡翅膀上打钉饰的男孩呢？",
    "prompt_language_text":"中文",
    
    # "default_infer_language":"中英混合",
    
    'default_pdf_path':r"D:\repos\pdf_voice_inference_webui\2308.04079v1.pdf",
    
    'server_port':51876,
    'client_port':51877,
}

with open(
    os.path.join(os.path.dirname(__file__), "config.json"), "w", encoding="utf-8"
) as f:
    f.write(json.dumps(config_list, ensure_ascii=False, indent=4))
