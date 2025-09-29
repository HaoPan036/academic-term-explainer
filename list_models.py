
import os
import google.generativeai as genai
from dotenv import load_dotenv

def list_my_models():
    """
    连接API并列出当前API Key可用的所有模型。
    """
    try:
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key or api_key == "YOUR_API_KEY_HERE":
            print("错误：在 .env 文件中未找到或未设置 GEMINI_API_KEY。")
            return

        genai.configure(api_key=api_key)

        print("正在为你的API Key获取可用模型列表...")
        print("------------------------------------")
        
        found_models = False
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(model.name)
                found_models = True

        print("------------------------------------")
        
        if not found_models:
            print("未找到任何支持 generateContent 的模型。")
        else:
            print("请从上面的列表中选择一个模型名称（例如 models/gemini-1.0-pro），然后告诉我。")

    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    list_my_models()
