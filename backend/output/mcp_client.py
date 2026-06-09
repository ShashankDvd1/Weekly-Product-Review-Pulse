import os
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

MCP_SERVER_PATH = "e:/PM_Portfolio_Projects/MCP-Server-For-Reviews-Analyzer/dist/index.js"

def format_report_data(app_name: str, report_data: list) -> str:
    lines = []
    lines.append(f"Weekly Product Review Pulse - {app_name}")
    lines.append("=" * 40)
    lines.append("")
    
    for idx, theme in enumerate(report_data, 1):
        lines.append(f"Theme {idx}: {theme.get('theme', 'Unknown')}")
        lines.append(f"Sentiment: {theme.get('sentiment', 'Neutral')} | Volume: {theme.get('volume', 0)}")
        lines.append(f"Summary: {theme.get('summary', '')}")
        
        examples = theme.get("example_reviews", [])
        if examples:
            lines.append("Examples:")
            for ex in examples:
                # remove newlines in example
                ex_clean = str(ex).replace('\n', ' ')
                lines.append(f" - {ex_clean}")
        lines.append("")
        lines.append("-" * 40)
        lines.append("")
        
    return "\n".join(lines)

async def push_via_mcp(app_name: str, report_data: list, team_category: str = None):
    # 1. Format content
    content = format_report_data(app_name, report_data)
    title = f"Weekly Product Review Pulse - {app_name}"

    # 2. Setup Stdio MCP Client
    server_params = StdioServerParameters(
        command="node",
        args=[MCP_SERVER_PATH]
    )

    result_data = None

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Call send_report
            arguments = {
                "title": title,
                "content": content
            }
            if team_category:
                arguments["team_name"] = team_category
                
            try:
                # call_tool returns a CallToolResult
                mcp_result = await session.call_tool("send_report", arguments=arguments)
                
                # Check for errors
                if mcp_result.isError:
                    raise Exception(f"MCP Tool Error: {mcp_result.content}")
                
                # Try parsing the result content
                if mcp_result.content and len(mcp_result.content) > 0:
                    text_result = mcp_result.content[0].text
                    try:
                        result_data = json.loads(text_result)
                    except json.JSONDecodeError:
                        result_data = {"status": "success", "output": text_result}
                else:
                    result_data = {"status": "success", "message": "No output returned"}
                    
            except Exception as e:
                raise Exception(f"Failed to execute send_report via MCP: {str(e)}")

    return result_data
