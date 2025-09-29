import os
import google.generativeai as genai
from dotenv import load_dotenv
import pkg_resources
from datetime import datetime
from time import sleep
from tqdm import tqdm
import sys

# --- 配置 ---
DEFAULT_SETTINGS = {
    "temperature": 0.7,
    "max_retries": 3,
    "retry_delay": 1
}


# --- 装饰器 ---
def retry_on_error(max_retries=3, delay=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    print(f"\n⚠️ 尝试失败 ({attempt + 1}/{max_retries})，{delay}秒后重试...", file=sys.stderr)
                    sleep(delay)
            return None

        return wrapper

    return decorator


# --- Agent核心 ---
class PaperExplainerAgent:
    """一个用于解释学术术语的、具备上下文感知能力的Agent。"""

    def __init__(self, field_of_study=None):
        """初始化Agent并配置API，同时记录研究领域。"""
        print("\n🔄 正在初始化系统...")
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "YOUR_API_KEY_HERE":
            raise ValueError("❌ GEMINI_API_KEY 未找到或未设置。请在 .env 文件中进行配置。")

        print("🔑 API密钥验证成功")
        genai.configure(api_key=api_key)

        print("🤖 正在连接到Gemini API...")
        self.model = genai.GenerativeModel('models/gemini-pro-latest')
        self.field_of_study = field_of_study
        self.history = []

        print("✅ Agent初始化成功！")
        if self.field_of_study:
            print(f"📚 当前研究领域: 【{self.field_of_study}】\n")

    def add_to_history(self, term, explanation):
        """添加查询记录到历史"""
        self.history.append({
            "term": term,
            "explanation": explanation,
            "timestamp": datetime.now(),
            "field": self.field_of_study
        })

    @retry_on_error(max_retries=DEFAULT_SETTINGS["max_retries"],
                    delay=DEFAULT_SETTINGS["retry_delay"])
    def explain(self, term, temperature=DEFAULT_SETTINGS["temperature"]):
        """根据上下文，使用Gemini API为给定术语生成解释。"""
        # 输入验证
        if not term or len(term.strip()) == 0:
            return "❌ 请输入有效的查询词"
        if len(term) > 100:
            return "❌ 查询词过长，请缩短后重试"

        # 动态构建Prompt
        base_prompt = f"""你是一个精准的AI学术助手。
你的任务是为科研人员提供一个术语的翻译、核心思想和应用实例。
不要使用任何Markdown格式（例如`**`或`*`）。"""

        if self.field_of_study:
            context_prompt = f"\n在 **{self.field_of_study}** 领域背景下，"
        else:
            context_prompt = ""

        style_prompt = f"""针对术语 '{term}'，严格按照以下格式，用换行符分隔，提供内容：
1. 领域翻译：[在该领域中最贴切的中文翻译]
2. 核心概括：[用一句话（不超过10个汉字）概括其核心思想]
3. 简明示例：[提供一个具体的、简单的例子来说明它的实际应用或工作原理]"""

        full_prompt = base_prompt + context_prompt + style_prompt

        try:
            print("\n🤔 正在分析中...", end="\r")
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature
                )
            )
            if not response.text:
                return "❌ 抱歉，Gemini 未能生成有效回答"

            explanation = response.text
            self.add_to_history(term, explanation)
            return explanation

        except Exception as e:
            return f"❌ 调用API时出错 ({e.__class__.__name__}): {str(e)}"


# --- 主程序逻辑 ---
def main():
    """运行单词解释器应用的主函数。"""
    print("\n" + "="*50)
    print("🎓 学术名词解释器 v2.0 (上下文感知版)")
    print("="*50 + "\n")

    try:
        lib_version = pkg_resources.get_distribution('google-generativeai').version
        print(f"📦 google-generativeai 版本: {lib_version}")
    except pkg_resources.DistributionNotFound:
        print("⚠️ 无法检测到 google-generativeai 的版本")

    user_field = input("\n🔍 请输入你当前研究的领域 (例如: LLM, 计算机视觉)\n   如果不需要，请直接按回车：").strip()

    try:
        agent = PaperExplainerAgent(field_of_study=user_field)
    except ValueError as e:
        print(f"\n❌ {e}")
        return

    print("\n💡 输入要查询的术语，输入 'quit' 退出\n")
    while True:
        term_to_explain = input("➤ ").strip()
        if term_to_explain.lower() == 'quit':
            print("\n👋 感谢使用，再见！")
            break

        if not term_to_explain:
            continue

        explanation = agent.explain(term_to_explain)
        print("\n📝 Gemini解释")
        print("="*30)
        print(explanation)
        print("="*30 + "\n")


if __name__ == "__main__":
    main()
