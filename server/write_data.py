import json, os

obj_list = [
    {
        "gpt_weight": r"D:\git_download\GPT-SoVITS-beta0217\GPT_weights\saileach-e15.ckpt",
        "sovits_weight": r"D:\git_download\GPT-SoVITS-beta0217\SoVITS_weights\saileach_e8_s232.pth",
        "lines": [
            {
                "ref_wav_path": r"D:\git_download\GPT-SoVITS-beta0217\pdf_inference_webui\server\slowed.wav",
                "prompt_text": "您是不是累了？这是我烤的甜司康饼。您可以坐下来，喝点茶，与我说说您的烦心事。",
                "prompt_language_text": "中文",
                "text": "Textpage content as a string in HTML format. This version contains complete formatting and positioning information. Images are included (encoded as base64 strings). You need an HTML package to interpret the output in Python. Your internet browser should be able to adequately display this information, but see Controlling Quality of HTML Output.",
                "text_language_text": "中英混合",
                'output_file_path':r"D:\git_download\GPT-SoVITS-beta0217\pdf_inference_webui\server\output.wav"
            },
        ],
    }
]
with open(
    os.path.join(os.path.dirname(__file__), "data.json"), "w", encoding="utf-8"
) as f:
    f.write(json.dumps(obj_list, ensure_ascii=False, indent=4))
