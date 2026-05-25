from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from neo4j import GraphDatabase
import re
from typing import List, Dict
import chromadb
from chromadb.utils import embedding_functions
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import uuid

# ===================== 配置项 =====================
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:7b"

# Neo4j
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "12345678"

# Chroma 配置（本地持久化模式）
CHROMA_PATH = "./chroma"
CHROMA_COLLECTION = "knowledge_documents"

# 向量模型（稠密检索 DVR）
EMBEDDING_MODEL = "BAAI/bge-small-zh-v1.5"

# BGE 重排序模型（Reranker）
RERANKER_MODEL = "BAAI/bge-reranker-v2-m3"

# 混合检索参数
TOP_K_VECTOR = 10  # 向量召回数量
TOP_K_BM25 = 10  # BM25召回数量
TOP_RERANK = 5  # 重排序后最终返回数量
# ===================================================

# ===================== 初始化服务 =====================
app = FastAPI(title="知识图谱混合检索", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 1. Neo4j 连接
class Neo4jConnection:
    def __init__(self, uri, user, pwd):
        self.driver = GraphDatabase.driver(uri, auth=(user, pwd))

    def close(self):
        self.driver.close()

    def create_entity(self, entity_name: str, entity_type: str):
        with self.driver.session() as session:
            session.run(
                """MERGE (e:Entity {name: $name}) SET e.type = $type""",
                name=entity_name, type=entity_type
            )

    def create_relationship(self, head: str, relation: str, tail: str):
        with self.driver.session() as session:
            session.run(
                """MATCH (h:Entity {name: $head}) MATCH (t:Entity {name: $tail}) MERGE (h)-[r:RELATION {name: $rel}]->(t)""",
                head=head, tail=tail, rel=relation
            )


neo4j = Neo4jConnection(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

# 2. Chroma 客户端连接
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBEDDING_MODEL
)
collection = chroma_client.get_or_create_collection(
    name=CHROMA_COLLECTION,
    embedding_function=embedding_func,
    metadata={"description": "知识文档混合检索库"}
)

# 3. BGE Reranker 重排序模型
device = "cuda" if torch.cuda.is_available() else "cpu"
rerank_tokenizer = AutoTokenizer.from_pretrained(RERANKER_MODEL)
rerank_model = AutoModelForSequenceClassification.from_pretrained(
    RERANKER_MODEL
).to(device).eval()


# ===================== 工具函数 =====================
def extract_entities_relations(text: str) -> List[Dict]:
    prompt = f"""
你是专业的知识图谱抽取引擎。
提取所有实体与关系，严格输出格式：
实体[类型], 关系, 实体[类型]
不要多余内容。
文本：{text}
"""
    data = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False, "temperature": 0.1}
    try:
        resp = requests.post(OLLAMA_URL, json=data)
        result = resp.json()["response"].strip()
        return parse_llm_output(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM调用失败：{str(e)}")


def parse_llm_output(output: str) -> List[Dict]:
    triples = []
    for line in output.strip().split("\n"):
        line = line.strip()
        if not line or line.count(",") < 2:
            continue
        try:
            parts = line.split(",")
            head_str, relation, tail_str = parts[0].strip(), parts[1].strip(), parts[2].strip()

            def extract(s):
                match = re.search(r"([^\[\]]+)\[([^\[\]]+)\]", s)
                return (match.group(1).strip(), match.group(2).strip()) if match else (s, "未知")

            h_name, h_type = extract(head_str)
            t_name, t_type = extract(tail_str)
            if h_name and t_name and relation:
                triples.append({
                    "head": h_name, "head_type": h_type,
                    "relation": relation,
                    "tail": t_name, "tail_type": t_type
                })
        except:
            continue
    return triples


def bge_rerank(query: str, docs: List[str]) -> List[Dict]:
    """BGE重排序：输入query+文档列表，输出按得分排序的结果"""
    pairs = [[query, doc] for doc in docs]
    with torch.no_grad():
        inputs = rerank_tokenizer(
            pairs, padding=True, truncation=True,
            max_length=512, return_tensors="pt"
        ).to(device)
        scores = rerank_model(**inputs).logits.squeeze(-1).cpu().numpy()

    ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
    return [{"document": doc, "score": float(score)} for doc, score in ranked]


# ===================== 请求结构体 =====================
class TextRequest(BaseModel):
    content: str


class SearchRequest(BaseModel):
    query: str


# ===================== 核心 API =====================
@app.post("/build-knowledge-graph", summary="构建知识图谱 + 写入Chroma")
def build_graph(req: TextRequest):
    text = req.content.strip()
    if not text:
        raise HTTPException(status_code=400, detail="文本不能为空")

    # 1. 提取三元组
    triples = extract_entities_relations(text)
    if not triples:
        return {"status": "ok", "msg": "未提取到实体关系", "data": []}

    # 2. 写入 Neo4j
    for t in triples:
        neo4j.create_entity(t["head"], t["head_type"])
        neo4j.create_entity(t["tail"], t["tail_type"])
        neo4j.create_relationship(t["head"], t["relation"], t["tail"])

    # 3. 写入 Chroma（支持向量检索 + BM25）
    collection.add(
        ids=[str(uuid.uuid4())],
        documents=[text],
        metadatas=[{"source": "knowledge_graph_build"}]
    )

    return {
        "status": "success",
        "msg": "图谱已保存到Neo4j，文档已存入Chroma",
        "count": len(triples),
        "triples": triples
    }


@app.post("/hybrid-search", summary="混合检索 HRM：向量 + BM25 + BGE重排")
def hybrid_search(req: SearchRequest):
    query = req.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="查询不能为空")

    # ========== 1. 稠密向量检索 DVR ==========
    vector_results = collection.query(
        query_texts=[query],
        n_results=TOP_K_VECTOR
    )
    vector_docs = vector_results["documents"][0] if vector_results["documents"] else []

    # ========== 2. BM25 检索（关键词统计） ==========
    bm25_results = collection.query(
        query_texts=[query],
        n_results=TOP_K_BM25,
        include=["documents"]
    )
    bm25_docs = bm25_results["documents"][0] if bm25_results["documents"] else []

    # ========== 3. 混合去重 ==========
    combined = list(set(vector_docs + bm25_docs))
    if not combined:
        return {"status": "ok", "msg": "无匹配结果", "data": []}

    # ========== 4. BGE 重排序（精排） ==========
    reranked = bge_rerank(query, combined)
    final = reranked[:TOP_RERANK]

    return {
        "status": "success",
        "query": query,
        "vector_recall": len(vector_docs),
        "bm25_recall": len(bm25_docs),
        "combined": len(combined),
        "final_result": final
    }


@app.get("/", summary="健康检查")
def index():
    return {"message": "知识图谱混合检索服务运行正常"}


# ===================== 启动 =====================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8718)