import asyncio
import json
from dotenv import load_env

# MCP sever imports
from mcp import types as mcp_types
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio

# ADK tool imports
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools import google_search
from google.adk.tools.mcp_tool.conversion_utils import adk_to_mcp_tool_type

load_env()

# preparing the gs tool
print("Initializing the Google Search tool")
adk_search_tool = FunctionTool(google_search)
print(f"ADK tool `{adk_search_tool.name}` initialized")

# MCP server setup
print("Creating MCP server")
app = Server("adk-google-search-server")


# Implement list tools handler
@app.list_tools()
async def list_tools() -> list[mcp_types.Tool]:
    """
    MCP handler to list available tools.
    """
    print("MCP Server: Received list_tools request")
    mcp_tool_schema = adk_to_mcp_tool_type(adk_search_tool)
    print(f"MCP Server: Advertising tool: {mcp_tool_schema.name}")
    return [mcp_tool_schema]


@app.call_tool()
async def call_tool(
    name: str, arguments: dict
) -> list[mcp_types.TextContent | mcp_types.ImageContent | mcp_types.EmbeddedResource]:
    """
    MCP handler to execute a tool call
    """
    print(
        f"MCP Server: Received a tool execution request for {name} with arguments {arguments}"
    )

    # check if the name matches our tool
    if name == adk_search_tool.name:
        try:
            adk_response = adk_search_tool.run_async(args=arguments, tool_context=None)
            print(f"MCP Server: Executed the tool {name} successfully")
            return adk_response
        except Exception as e:
            print(f"MCP Server: Error executing ADK tool '{name}': {e}")
            error_text = json.dumps(
                {"error": f"Failed to execute tool '{name}': {str(e)}"}
            )
            return [mcp_types.TextContent(type="text", text=error_text)]
    else:
        # Handle calls to unknown tools
        print(f"MCP Server: Tool '{name}' not found.")
        error_text = json.dumps({"error": f"Tool '{name}' not implemented."})
        # Returning error as TextContent for simplicity
        return [mcp_types.TextContent(type="text", text=error_text)]


# --- MCP Server Runner ---
async def run_server():
    """Runs the MCP server over standard input/output."""
    # Use the stdio_server context manager from the MCP library
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        print("MCP Server starting handshake...")
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=app.name,  # Use the server name defined above
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    # Define server capabilities - consult MCP docs for options
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
        print("MCP Server run loop finished.")


if __name__ == "__main__":
    print("Launching MCP Server exposing ADK tools...")
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        print("\nMCP Server stopped by user.")
    except Exception as e:
        print(f"MCP Server encountered an error: {e}")
    finally:
        print("MCP Server process exiting.")
# --- End MCP Server ---
