import os
import google.generativeai as genai
from dotenv import load_dotenv
import pkg_resources
from datetime import datetime
from time import sleep
from tqdm import tqdm

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
                    print(f"尝试失败，{delay}秒后重试...")
                    sleep(delay)
            return None

        return wrapper

    return decorator


# --- Agent核心 ---
class PaperExplainerAgent:
    """一个用于解释学术术语的、具备上下文感知能力的Agent。"""

    def __init__(self, field_of_study=None):
        """初始化Agent并配置API，同时记录研究领域。"""
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "YOUR_API_KEY_HERE":
            raise ValueError("GEMINI_API_KEY 未找到或未设置。请在 .env 文件中进行配置。")
        genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel('gemini-pro')
        self.field_of_study = field_of_study
        self.history = []

        print("Agent初始化成功，已连接到Gemini。")
        if self.field_of_study:
            print(f"已设定当前研究领域为: 【{self.field_of_study}】")

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
            return "请输入有效的查询词"
        if len(term) > 100:
            return "查询词过长，请缩短后重试"

        # 动态构建Prompt
        base_prompt = f"""你是一位风趣幽默、知识渊博的学术导师。
你的任务是向一位充满好奇心的科研新手解释学术术语 '{term}'。"""

        if self.field_of_study:
            context_prompt = f"\n请特别侧重于它在 **{self.field_of_study}** 领域中的含义和应用。"
        else:
            context_prompt = ""

        style_prompt = f"""
请用生动、易懂、且带有一点比喻的方式来解释，像是在轻松的对话，而不是在念教科书。
请用以下结构来回答：
1.  **一句话解释：**首先，用一句话概括这个术语的核心思想。
2.  **深入浅出：**然后，用一个简单的比喻或生活中的例子来详细说明。
3.  **学术背景：**最后，可以稍微提一下它在学术领域中的具体作用或重要性。"""

        full_prompt = base_prompt + context_prompt + style_prompt

        try:
            print("正在思考中...", end="\r")
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature
                )
            )
            if not response.text:
                return "抱歉，Gemini 未能生成有效回答"

            explanation = response.text
            self.add_to_history(term, explanation)
            return explanation

        except Exception as e:
            return f"调用API时出错 ({e.__class__.__name__}): {str(e)}"


# --- 主程序逻辑 ---
def main():
    """运行单词解释器应用的主函数。"""
    try:
        lib_version = pkg_resources.get_distribution('google-generativeai').version
        print(f"--- 加载的 google-generativeai 版本: {lib_version} ---")
    except pkg_resources.DistributionNotFound:
        print("--- 无法检测到 google-generativeai 的版本。 ---")

    print("--- 学术名词解释器 v2.0 (上下文感知版) ---")

    # 启动时获取上下文
    user_field = input("请输入你当前研究的领域 (例如: LLM, 计算机视觉)，如果不需要，请直接按回车：").strip()

    try:
        agent = PaperExplainerAgent(field_of_study=user_field)
    except ValueError as e:
        print(f"错误: {e}")
        return

    print("\n输入你想查询的单词，或者输入 'quit' 退出。")
    while True:
        term_to_explain = input("> ").strip()
        if term_to_explain.lower() == 'quit':
            print("再见！")
            break

        if not term_to_explain:
            continue

        print(f"\n正在查询 '{term_to_explain}'...")
        explanation = agent.explain(term_to_explain)
        print(f"\n--- Gemini的解释 ---")
        print(explanation)
        print("---------------------\n")


if __name__ == "__main__":
    main()
