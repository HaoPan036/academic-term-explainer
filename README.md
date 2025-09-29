
# 学术名词解释器 (Academic Word Explainer)

这是一个使用 Google Gemini API 构建的简单 AI Agent，旨在帮助科研新手理解学术文献中出现的复杂术语。

## 功能
- 输入一个学术术语，获取通俗易懂的解释。
- Agent 被设计成一位风趣幽默的学术导师，让学习过程不再枯燥。

## 安装与配置

1.  **克隆或下载项目**
    - 将本项目所有文件下载到你的电脑上。

2.  **配置API密钥**
    - 找到 `.env` 文件。
    - 访问 [Google AI Studio](https://aistudio.google.com/app/apikey) 获取你的 Gemini API 密钥。
    - 将你的密钥粘贴到 `.env` 文件中，替换 `YOUR_API_KEY_HERE`。

3.  **安装依赖**
    - 在你的项目文件夹中打开终端（例如在 PyCharm 的终端中）。
    - 运行以下命令来安装所有必需的库：
      ```bash
      pip install -r requirements.txt
      ```

## 如何运行

- 在终端中，运行主程序：
  ```bash
  python3 word_explainer.py
  ```
- 程序启动后，根据提示输入你想要查询的术语即可。

---

## 问题排查 (Troubleshooting)

### 错误: `404 models/... is not found ...`

这是最常见的问题，它意味着你的 API 密钥有权限，但它能访问的模型列表与代码中默认的 `models/gemini-pro-latest` 不同。

**解决方案：**

1.  **运行模型列表脚本**：
    - 首先，运行我们项目中的 `list_models.py` 脚本：
      ```bash
      python3 list_models.py
      ```
    - 这个脚本会打印出你的 API 密钥**真正能够使用**的所有模型的列表。

2.  **选择并更新模型**：
    - 从打印出的列表中，选择一个看起来合适的模型名称（例如，`models/gemini-pro-latest` 或其他可用的 `pro` 或 `flash` 模型）。
    - 打开 `word_explainer.py` 文件。
    - 找到下面这行代码：
      ```python
      self.model = genai.GenerativeModel('models/gemini-pro-latest')
      ```
    - 将 `'models/gemini-pro-latest'` 替换为你从列表中选择的新模型名称。
    - 保存文件，然后重新运行 `word_explainer.py`，问题应该就解决了。
