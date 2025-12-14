import asyncio
import traceback
from typing import Annotated, Any

from langchain_core.tools import StructuredTool, tool
# 网页搜索功能已移除，不再需要 TavilySearch
from pydantic import BaseModel, Field

from src import config, graph_base, knowledge_base
from src.utils import logger


class GraphQueryModel(BaseModel):
    query: str = Field(description="要在知识图谱中检索的关键词。")


class GraphStatisticsModel(BaseModel):
    """知识图谱统计工具的参数模型"""
    keyword: str = Field(description="要统计的关键词，如'重力坝'、'病害'、'裂缝'等。")
    stat_type: str = Field(
        default="count_related",
        description="统计类型：count_related(统计相关实体数量)、count_by_type(按类型分组统计)、list_entities(列出具体实体名称)"
    )


def get_static_tools(input_context: dict | None = None) -> list:
    """注册静态工具"""
    retrieval_mode = input_context.get("retrieval_mode", "mix") if input_context else "mix"
    # 知识库检索/大模型检索不暴露图谱工具
    if retrieval_mode in ("local", "llm"):
        return []

    graph_name = (input_context or {}).get("graph_name") or "neo4j"

    async def graph_search(query: str) -> Any:
        try:
            logger.debug(f"Querying knowledge graph [{graph_name}] with: {query}")
            result = graph_base.query_node(query, hops=2, kgdb_name=graph_name, return_format="triples")
            return result
        except Exception as e:
            logger.error(f"Knowledge graph query error: {e}, {traceback.format_exc()}")
            return f"知识图谱查询失败: {str(e)}"

    async def graph_statistics(keyword: str, stat_type: str = "count_related") -> Any:
        """知识图谱统计工具 - 用于回答统计性问题"""
        try:
            logger.debug(f"统计知识图谱 [{graph_name}] 关键词: {keyword}, 类型: {stat_type}")
            
            if not graph_base.is_running():
                return "知识图谱数据库未连接，无法进行统计查询。"
            
            graph_base.use_database(graph_name)
            
            with graph_base.driver.session() as session:
                if stat_type == "count_related":
                    # 统计与关键词相关的实体数量
                    result = session.run("""
                        MATCH (n:Entity)
                        WHERE toLower(n.entity_id) CONTAINS toLower($keyword)
                        WITH count(n) as direct_count
                        OPTIONAL MATCH (n:Entity)-[r:RELATION]-(m:Entity)
                        WHERE toLower(n.entity_id) CONTAINS toLower($keyword)
                        WITH direct_count, count(DISTINCT m) as related_count, count(r) as relation_count
                        RETURN direct_count, related_count, relation_count
                    """, keyword=keyword).single()
                    
                    direct = result["direct_count"] if result else 0
                    related = result["related_count"] if result else 0
                    relations = result["relation_count"] if result else 0
                    
                    return (
                        f"【知识图谱统计结果】\n"
                        f"关键词：{keyword}\n"
                        f"- 直接包含'{keyword}'的实体数量：{direct} 个\n"
                        f"- 与'{keyword}'相关联的实体数量：{related} 个\n"
                        f"- 相关的关系数量：{relations} 条\n"
                        f"- 总计涉及实体：{direct + related} 个"
                    )
                
                elif stat_type == "count_by_type":
                    # 按关系类型分组统计
                    results = session.run("""
                        MATCH (n:Entity)-[r:RELATION]->(m:Entity)
                        WHERE toLower(n.entity_id) CONTAINS toLower($keyword) 
                           OR toLower(m.entity_id) CONTAINS toLower($keyword)
                        RETURN r.type as relation_type, count(*) as count
                        ORDER BY count DESC
                        LIMIT 20
                    """, keyword=keyword)
                    
                    stats = []
                    total = 0
                    for record in results:
                        rel_type = record["relation_type"] or "未知类型"
                        count = record["count"]
                        total += count
                        stats.append(f"  - {rel_type}: {count} 条")
                    
                    if not stats:
                        return f"未找到与'{keyword}'相关的统计数据。"
                    
                    return (
                        f"【知识图谱分类统计】\n"
                        f"关键词：{keyword}\n"
                        f"按关系类型统计（共 {total} 条关系）：\n" + "\n".join(stats)
                    )
                
                elif stat_type == "list_entities":
                    # 列出具体实体名称
                    results = session.run("""
                        MATCH (n:Entity)
                        WHERE toLower(n.entity_id) CONTAINS toLower($keyword)
                        RETURN DISTINCT n.entity_id as entity_name
                        ORDER BY entity_name
                        LIMIT 50
                    """, keyword=keyword)
                    
                    entities = [record["entity_name"] for record in results]
                    
                    if not entities:
                        return f"未找到包含'{keyword}'的实体。"
                    
                    entity_list = "\n".join([f"  {i+1}. {e}" for i, e in enumerate(entities)])
                    return (
                        f"【知识图谱实体列表】\n"
                        f"关键词：{keyword}\n"
                        f"共找到 {len(entities)} 个相关实体：\n{entity_list}"
                        + (f"\n（仅显示前50个）" if len(entities) == 50 else "")
                    )
                
                else:
                    return f"不支持的统计类型: {stat_type}，支持的类型: count_related, count_by_type, list_entities"
                    
        except Exception as e:
            logger.error(f"知识图谱统计错误: {e}, {traceback.format_exc()}")
            return f"知识图谱统计查询失败: {str(e)}"

    graph_tool = StructuredTool.from_function(
        coroutine=graph_search,
        name="global_knowledge_graph_search",
        description=f"使用全局知识图谱（数据库：{graph_name}）进行检索，查询实体间的关联关系和知识信息。",
        args_schema=GraphQueryModel,
        metadata={"graph_name": graph_name, "tag": ["knowledge_graph"]},
    )

    statistics_tool = StructuredTool.from_function(
        coroutine=graph_statistics,
        name="knowledge_graph_statistics",
        description=(
            f"使用知识图谱（数据库：{graph_name}）进行统计查询。"
            "当用户询问'有多少'、'数量是多少'、'统计一下'、'一共有几个'等统计性问题时，优先使用此工具。"
            "可以统计与关键词相关的实体数量、按类型分组统计、或列出具体实体名称。"
        ),
        args_schema=GraphStatisticsModel,
        metadata={"graph_name": graph_name, "tag": ["knowledge_graph", "statistics"]},
    )

    static_tools = [
        graph_tool,
        statistics_tool,
    ]

    # 网页搜索功能已移除，只保留知识库相关功能

    return static_tools


class KnowledgeRetrieverModel(BaseModel):
    query_text: str = Field(
        description=(
            "查询的关键词，查询的时候，应该尽量以可能帮助回答这个问题的关键词进行查询，不要直接使用用户的原始输入去查询。"
        )
    )


def get_kb_based_tools(input_context: dict = None) -> list:
    """获取所有知识库基于的工具"""
    retrieval_mode = input_context.get("retrieval_mode", "mix") if input_context else "mix"
    if retrieval_mode in ("global", "llm"):
        return []

    # 获取所有知识库
    kb_tools = []
    retrievers = knowledge_base.get_retrievers()

    # 从输入上下文中获取检索模式，默认为 "mix"
    raw_whitelist = input_context.get("kb_whitelist") if input_context else []
    if isinstance(raw_whitelist, str):
        raw_whitelist = [raw_whitelist]
    kb_whitelist = set(raw_whitelist or [])

    def _create_retriever_wrapper(db_id: str, retriever_info: dict[str, Any]):
        """创建检索器包装函数的工厂函数，避免闭包变量捕获问题"""

        async def async_retriever_wrapper(query_text: str) -> Any:
            """异步检索器包装函数"""
            retriever = retriever_info["retriever"]
            try:
                logger.debug(f"Retrieving from database {db_id} with query: {query_text}, mode: {retrieval_mode}")
                if asyncio.iscoroutinefunction(retriever):
                    result = await retriever(query_text, mode=retrieval_mode)
                else:
                    result = retriever(query_text, mode=retrieval_mode)
                logger.debug(f"Retrieved {len(result) if isinstance(result, list) else 'N/A'} results from {db_id}")
                return result
            except Exception as e:
                logger.error(f"Error in retriever {db_id}: {e}")
                return f"检索失败: {str(e)}"

        return async_retriever_wrapper

    for db_id, retrieve_info in retrievers.items():
        if kb_whitelist and db_id not in kb_whitelist:
            continue
        try:
            # 使用改进的工具ID生成策略
            tool_id = f"query_{db_id[:8]}"

            # 构建工具描述
            description = (
                f"使用 {retrieve_info['name']} 知识库进行检索。\n"
                f"下面是这个知识库的描述：\n{retrieve_info['description'] or '没有描述。'} "
            )

            # 使用工厂函数创建检索器包装函数，避免闭包问题
            retriever_wrapper = _create_retriever_wrapper(db_id, retrieve_info)

            # 使用 StructuredTool.from_function 创建异步工具
            tool = StructuredTool.from_function(
                coroutine=retriever_wrapper,
                name=tool_id,
                description=description,
                args_schema=KnowledgeRetrieverModel,
                metadata=retrieve_info["metadata"] | {"tag": ["knowledgebase"]},
            )

            kb_tools.append(tool)
            # logger.debug(f"Successfully created tool {tool_id} for database {db_id}")

        except Exception as e:
            logger.error(f"Failed to create tool for database {db_id}: {e}, \n{traceback.format_exc()}")
            continue

    return kb_tools


def get_buildin_tools(input_context: dict = None) -> list:
    """获取所有可运行的工具（给大模型使用）"""
    tools = []

    try:
        # 获取所有知识库基于的工具
        tools.extend(get_kb_based_tools(input_context))
        tools.extend(get_static_tools(input_context))

        # MySQL工具已移除，只保留知识库相关功能
        # 如需数据库功能，请手动配置

    except Exception as e:
        logger.error(f"Failed to get knowledge base retrievers: {e}")

    return tools


def gen_tool_info(tools) -> list[dict[str, Any]]:
    """获取所有工具的信息（用于前端展示）"""
    tools_info = []

    try:
        # 获取注册的工具信息
        for tool_obj in tools:
            try:
                metadata = getattr(tool_obj, "metadata", {}) or {}
                info = {
                    "id": tool_obj.name,
                    "name": metadata.get("name", tool_obj.name),
                    "description": tool_obj.description,
                    "metadata": metadata,
                    "args": [],
                    # "is_async": is_async  # Include async information
                }

                if hasattr(tool_obj, "args_schema") and tool_obj.args_schema:
                    schema = tool_obj.args_schema.schema()
                    for arg_name, arg_info in schema.get("properties", {}).items():
                        info["args"].append(
                            {
                                "name": arg_name,
                                "type": arg_info.get("type", ""),
                                "description": arg_info.get("description", ""),
                            }
                        )

                tools_info.append(info)
                # logger.debug(f"Successfully processed tool info for {tool_obj.name}")

            except Exception as e:
                logger.error(
                    f"Failed to process tool {getattr(tool_obj, 'name', 'unknown')}: {e}\n{traceback.format_exc()}"
                )
                continue

    except Exception as e:
        logger.error(f"Failed to get tools info: {e}\n{traceback.format_exc()}")
        return []

    logger.info(f"Successfully extracted info for {len(tools_info)} tools")
    return tools_info
