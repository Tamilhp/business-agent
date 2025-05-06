from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters


async def create_agent():
    """Get tools from MCP server"""
    tools, exit_stack = await MCPToolset.from_server(
        connection_params=StdioServerParameters(
            command = 'npx',
            args=["y", "@modelcontextprotocol/server-filesystem", "/Users/tamil/work/business-agent"],
        )
    )

    agent = LlmAgent(
      model='gemini-2.0-flash',
      name='enterprise_assistant',
      instruction=(
          'Help user accessing their file systems'
      ),
      tools=tools,
  )
    return agent, exit_stack
