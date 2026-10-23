#!/usr/bin/env python3
"""Standard Model Context Protocol (MCP) server for Hermes Agent (Jarvis).

Exposes native tools to delegate coding tasks, inspect system status, and switch
division branches directly from Telegram or Hermes CLI.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add workspace to path
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from mcp.server import Server
import mcp.types as types
import mcp.server.stdio

from harmage.bridge_engine import (
    delegate_task,
    get_task_status,
    list_delegated_tasks,
    switch_division_branch,
    get_system_overview,
)

server = Server("antigravity-bridge")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """Expose delegation and management tools to Hermes."""
    return [
        types.Tool(
            name="delegate_to_antigravity",
            description=(
                "Delegate heavy coding, software engineering, bug fixing, scriptwriting, "
                "or video assembly to Antigravity (Google AI Pro IDE). Use this whenever the "
                "user on Telegram asks for new features, bug fixes, or code creation to avoid "
                "burning your Telegram bot tokens."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "task_title": {
                        "type": "string",
                        "description": "Short, clear title of the task."
                    },
                    "task_description": {
                        "type": "string",
                        "description": "Detailed requirements, file paths, endpoints, or specs for Antigravity."
                    },
                    "division": {
                        "type": "string",
                        "enum": [
                            "content_creator",
                            "coding",
                            "video_longform",
                            "treasury",
                            "executive",
                            "qa"
                        ],
                        "description": "The division branch responsible (e.g. content_creator for TikTok affiliate, coding for dev)."
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["urgent", "high", "normal", "low"],
                        "description": "Priority level (default: high)."
                    }
                },
                "required": ["task_title", "task_description"]
            }
        ),
        types.Tool(
            name="check_antigravity_task",
            description="Check progress, completion status, or output of a previously delegated task.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Specific task ID (e.g. TSK-AGY-XXXXXX) or 'latest' for the most recent."
                    }
                }
            }
        ),
        types.Tool(
            name="get_harmage_system_overview",
            description="Inspect running status of all 6 Harmage & Hermes servers and view live token budget balance.",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="switch_division_branch",
            description="Switch the active Git branch to a specific Harmage division workspace.",
            inputSchema={
                "type": "object",
                "properties": {
                    "division": {
                        "type": "string",
                        "enum": [
                            "content_creator",
                            "coding",
                            "video_longform",
                            "treasury",
                            "executive",
                            "qa"
                        ],
                        "description": "Target division branch."
                    }
                },
                "required": ["division"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    """Execute tool requests dispatched by Jarvis / Hermes."""
    args = arguments or {}

    try:
        if name == "delegate_to_antigravity":
            title = args.get("task_title", "Untitled Task")
            desc = args.get("task_description", "")
            division = args.get("division", "coding")
            priority = args.get("priority", "high")
            
            result = delegate_task(
                title=title,
                description=desc,
                division=division,
                priority=priority,
                requested_by="Jarvis (Telegram / MCP)"
            )
            return [types.TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]

        elif name == "check_antigravity_task":
            task_id = args.get("task_id", "latest")
            status = get_task_status(task_id)
            return [types.TextContent(type="text", text=json.dumps(status, indent=2, ensure_ascii=False))]

        elif name == "get_harmage_system_overview":
            overview = get_system_overview()
            return [types.TextContent(type="text", text=json.dumps(overview, indent=2, ensure_ascii=False))]

        elif name == "switch_division_branch":
            division = args.get("division", "coding")
            sw_res = switch_division_branch(division)
            return [types.TextContent(type="text", text=json.dumps(sw_res, indent=2, ensure_ascii=False))]

        else:
            return [types.TextContent(type="text", text=f"Error: Unknown tool '{name}'")]

    except Exception as e:
        return [types.TextContent(type="text", text=f"Tool Execution Error: {str(e)}")]


async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
