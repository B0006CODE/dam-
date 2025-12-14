import os

from ..config import config
from .factory import KnowledgeBaseFactory
from .graph import GraphDatabase
from .implementations.lightrag import LightRagKB
from .implementations.milvus import MilvusKB
from .manager import KnowledgeBaseManager

# 注册知识库类型（只保留 Milvus 和 LightRAG）
KnowledgeBaseFactory.register("milvus", MilvusKB, {"description": "基于 Milvus 的生产级向量知识库，支持高性能向量检索"})
KnowledgeBaseFactory.register("lightrag", LightRagKB, {"description": "基于图检索的知识库，支持实体关系构建和复杂查询"})

# 创建知识库管理器
work_dir = os.path.join(config.save_dir, "knowledge_base_data")
knowledge_base = KnowledgeBaseManager(work_dir)

# 创建图数据库实例
graph_base = GraphDatabase()

__all__ = ["GraphDatabase", "knowledge_base", "graph_base"]
