import os
import requests
from pypdf import PdfReader

# -------------------------- 配置项 --------------------------
OLLAMA_EMBEDDING_API = "http://localhost:11434/api/embeddings"  # Ollama 默认地址
EMBEDDING_MODEL = "nomic-embed-text"  # 使用的 Embedding 模型
# -------------------------------------------------------------

def read_text_file(file_path: str) -> str:
    """
    读取 .txt / .md 文本文件
    :param file_path: 文件路径
    :return: 文件纯文本内容
    """
    try:
        # 支持 utf-8 编码，遇到异常编码自动忽略
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        print(f"读取文本文件失败: {e}")
        return ""

def read_pdf_file(file_path: str) -> str:
    """
    读取 .pdf 文件（提取所有页面文本）
    :param file_path: 文件路径
    :return: PDF 纯文本内容
    """
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        print(f"读取 PDF 文件失败: {e}")
        return ""

def get_file_content(file_path: str) -> str:
    """
    自动根据文件后缀读取对应格式文件
    支持：.txt / .md / .pdf
    """
    if not os.path.exists(file_path):
        print(f"错误：文件不存在 {file_path}")
        return ""

    ext = os.path.splitext(file_path)[-1].lower()

    if ext in [".txt", ".md"]:
        return read_text_file(file_path)
    elif ext == ".pdf":
        return read_pdf_file(file_path)
    else:
        print(f"不支持的文件格式: {ext}")
        return ""

def generate_ollama_embedding(text: str) -> list:
    """
    调用 Ollama API 生成文本 Embedding 向量
    :param text: 待向量化的文本
    :return: 浮点数向量列表
    """
    if not text:
        return []

    payload = {
        "model": EMBEDDING_MODEL,
        "prompt": text.strip()
    }

    try:
        response = requests.post(OLLAMA_EMBEDDING_API, json=payload)
        response.raise_for_status()  # 抛出 HTTP 异常
        result = response.json()
        return result.get("embedding", [])
    except Exception as e:
        print(f"生成 Embedding 失败: {e}")
        return []

# -------------------------- 使用示例 --------------------------
if __name__ == "__main__":
    # 替换为你的本地文件路径
    FILE_PATH = "test.pdf"  # 也可以是 test.txt / test.md

    # 1. 读取文件内容
    content = get_file_content(FILE_PATH)
    if not content:
        exit("文件内容为空，退出程序")

    print(f"✅ 成功读取文件，文本长度：{len(content)} 字符")
    print("-" * 50)

    # 2. 生成 Embedding 向量
    embedding = generate_ollama_embedding(content)
    if embedding:
        print(f"✅ 成功生成 Embedding")
        print(f"向量维度：{len(embedding)}")
        print(f"向量前5个值：{embedding[:5]}")
    else:
        print("❌ Embedding 生成失败")