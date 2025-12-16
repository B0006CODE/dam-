# 项目简介

Smart Water 是基于知识图谱和向量数据库的专业水利工程知识管理平台。系统结合了先进的自然语言处理技术和知识图谱技术，为水利大坝安全监测、隐患处理、智能问答等应用场景提供全面的技术支持。

### 技术栈选择

- **后端服务**: [FastAPI](https://github.com/tiangolo/fastapi) + Python 3.11+
- **前端界面**: [Vue.js 3](https://github.com/vuejs/vue) + [Ant Design Vue](https://github.com/vueComponent/ant-design-vue)
- **数据库存储**: [SQLite](https://github.com/sqlite/sqlite) + [MinIO](https://github.com/minio/minio)
- **知识存储**: [Milvus](https://github.com/milvus-io/milvus)、[Chroma](https://github.com/chroma-core/chroma)（向量数据库）+ [Neo4j](https://github.com/neo4j/neo4j)（图数据库）
- **智能体框架**: [LangGraph](https://github.com/langchain-ai/langgraph)
- **文档解析**: [LightRAG](https://github.com/HKUDS/LightRAG) + [MinerU](https://github.com/HKUDS/MinerU) + [PP-Structure-V3](https://github.com/PaddlePaddle/PaddleOCR)
- **容器编排**: [Docker Compose](https://github.com/docker/compose)

### 核心功能

- **智能问答**: 支持多种大语言模型，提供专业领域的智能对话和问答服务
- **知识库管理**: 支持多种存储形式（Chroma、Milvus、LightRAG），高效管理水利专业知识
- **知识图谱**: 自动构建和可视化知识图谱，支持图查询和关联分析
- **文档解析**: 支持 PDF、Word、图片等多种格式的智能解析
- **权限管理**: 三级权限体系（超级管理员、专业用户、普通用户）
- **内容安全**: 内置内容审查机制，保障服务合规性

### 系统特色

- **专业领域适配**: 针对水利大坝安全场景深度优化
- **高性能检索**: 向量数据库支持快速语义搜索
- **可视化分析**: 直观的知识图谱展示和数据分析看板
- **灵活部署**: 支持Docker容器化部署，易于维护和扩展