from typing import Any, cast

from langchain_core.messages import AIMessage, ToolMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.runtime import Runtime

from src.agents.common.base import BaseAgent
from src.agents.common.mcp import get_mcp_tools
from src.agents.common.models import load_chat_model
from src.utils import logger

from .context import Context
from .state import State
from .tools import get_tools


class ChatbotAgent(BaseAgent):
    name = "智能体助手"
    description = "基础的对话机器人，可以回答问题，默认不使用任何工具，可在配置中启用需要的工具。"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.graph = None
        self.checkpointer = None
        self.context_schema = Context

    def get_tools(self, runtime: Runtime[Context] = None):
        input_context = runtime.config.configurable if runtime and hasattr(runtime, 'config') and hasattr(runtime.config, 'configurable') else None
        return get_tools(input_context)

    async def _get_invoke_tools(self, selected_tools: list[str], selected_mcps: list[str], runtime: Runtime[Context] = None):
        """根据配置获取工具。
        工具注入根据 retrieval_mode 进行过滤：
        - llm: 不注入任何工具（纯大模型回答）
        - local: 只注入知识库相关工具（不包括图谱工具）
        - global: 只注入知识图谱相关工具（不包括知识库工具）
        - mix: 注入所有工具
        """
        # 获取 retrieval_mode
        try:
            input_context = runtime.config.configurable if runtime and hasattr(runtime, 'config') and hasattr(runtime.config, 'configurable') else None
            retrieval_mode = input_context.get("retrieval_mode", "mix") if input_context else "mix"
        except Exception:
            retrieval_mode = "mix"
        
        logger.info(f"_get_invoke_tools called with retrieval_mode: {retrieval_mode}")
        
        # 在 llm 模式下，不注入任何工具（包括 MCP）
        if retrieval_mode == "llm":
            logger.info("LLM mode: returning empty tools")
            return []
        
        # 每次都重新获取工具，不使用缓存，以确保根据当前 retrieval_mode 获取正确的工具
        # get_tools 内部会调用 get_buildin_tools，它会根据 retrieval_mode 过滤工具
        all_tools = self.get_tools(runtime)
        
        # 图谱相关工具名称
        core_graph_tool_names = {"global_knowledge_graph_search", "knowledge_graph_statistics"}
        
        enabled_tools = []
        
        if retrieval_mode == "local":
            # local 模式：只使用知识库工具，排除所有图谱工具
            enabled_tools = [tool for tool in all_tools if tool.name not in core_graph_tool_names]
            logger.info(f"Local mode: filtered out graph tools, remaining: {[t.name for t in enabled_tools]}")
        elif retrieval_mode == "global":
            # global 模式：只使用图谱工具
            enabled_tools = [tool for tool in all_tools if tool.name in core_graph_tool_names]
            logger.info(f"Global mode: only graph tools: {[t.name for t in enabled_tools]}")
        else:
            # mix 模式：使用所有工具
            enabled_tools = all_tools
            logger.info(f"Mix mode: using all tools: {[t.name for t in enabled_tools]}")
        
        # 如果有 selected_tools 配置，进一步过滤
        if selected_tools and isinstance(selected_tools, list) and len(selected_tools) > 0:
            # 只保留在 selected_tools 中的工具，但仍需遵守 retrieval_mode 的限制
            if retrieval_mode == "local":
                enabled_tools = [tool for tool in enabled_tools 
                                if tool.name in selected_tools and tool.name not in core_graph_tool_names]
            elif retrieval_mode == "global":
                enabled_tools = [tool for tool in enabled_tools 
                                if tool.name in selected_tools or tool.name in core_graph_tool_names]
            else:
                enabled_tools = [tool for tool in enabled_tools if tool.name in selected_tools]
            
            # mix 和 global 模式确保核心图谱工具始终可用
            if retrieval_mode in ("mix", "global"):
                existing_names = {t.name for t in enabled_tools}
                for tool in all_tools:
                    if tool.name in core_graph_tool_names and tool.name not in existing_names:
                        enabled_tools.append(tool)
        
        # 处理 MCP 工具
        if selected_mcps and isinstance(selected_mcps, list) and len(selected_mcps) > 0:
            for mcp in selected_mcps:
                enabled_tools.extend(await get_mcp_tools(mcp))

        logger.info(f"Final enabled tools for {retrieval_mode} mode: {[t.name for t in enabled_tools]}")
        return enabled_tools

    async def llm_call(self, state: State, runtime: Runtime[Context] = None) -> dict[str, Any]:
        """调用 llm 模型 - 异步版本以支持异步工具"""
        model = load_chat_model(runtime.context.model)

        # 这里要根据配置动态获取工具
        available_tools = await self._get_invoke_tools(runtime.context.tools, runtime.context.mcps, runtime)
        logger.info(f"LLM binded ({len(available_tools)}) available_tools: {[tool.name for tool in available_tools]}")

        if available_tools:
            model = model.bind_tools(available_tools)

        # 使用异步调用
        response = cast(
            AIMessage,
            await model.ainvoke([{"role": "system", "content": runtime.context.system_prompt}, *state.messages]),
        )
        return {"messages": [response]}

    async def dynamic_tools_node(self, state: State, runtime: Runtime[Context]) -> dict[str, list[ToolMessage]]:
        """Execute tools dynamically based on configuration.

        This function gets the available tools based on the current configuration
        and executes the requested tool calls from the last message.
        """
        # Get available tools based on configuration
        available_tools = await self._get_invoke_tools(runtime.context.tools, runtime.context.mcps, runtime)

        # Create a ToolNode with the available tools
        tool_node = ToolNode(available_tools)

        # Execute the tool node
        result = await tool_node.ainvoke(state)

        return cast(dict[str, list[ToolMessage]], result)

    async def get_graph(self, **kwargs):
        """构建图"""
        if self.graph:
            return self.graph

        builder = StateGraph(State, context_schema=self.context_schema)
        builder.add_node("chatbot", self.llm_call)
        builder.add_node("tools", self.dynamic_tools_node)
        builder.add_edge(START, "chatbot")
        builder.add_conditional_edges(
            "chatbot",
            tools_condition,
        )
        builder.add_edge("tools", "chatbot")
        builder.add_edge("chatbot", END)

        self.checkpointer = await self._get_checkpointer()
        graph = builder.compile(checkpointer=self.checkpointer, name=self.name)
        self.graph = graph
        return graph


def main():
    pass


if __name__ == "__main__":
    main()
    # asyncio.run(main())
