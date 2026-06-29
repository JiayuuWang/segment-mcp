# Copyright (c) 2026 Dedalus Labs, Inc. and its contributors
# SPDX-License-Identifier: MIT

"""End-to-end client test for the Segment MCP server.

Required environment variables:
    DEDALUS_API_KEY   dsk-live-...
    SEGMENT_API_KEY   Segment public API key

Optional:
    MCP_SERVER_SLUG   default: JiayuWang/segment-mcp

Usage:
    python src/_client.py
"""

import asyncio
import os
import sys

from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from segment import segment  # noqa: E402
from dedalus_mcp.auth import Connection as _Conn
from dedalus_labs.lib.mcp.request import slug_to_connection_name as _s2c


def _rebind(conn, slug):
    return _Conn(name=_s2c(slug), secrets=conn.secrets, base_url=conn.base_url,
                 auth_header_name=conn.auth_header_name, auth_header_format=conn.auth_header_format)


DEDALUS_API_KEY = os.getenv("DEDALUS_API_KEY", "")
DEDALUS_API_URL = os.getenv("DEDALUS_API_URL", "https://api.dedaluslabs.ai")
DEDALUS_AS_URL  = os.getenv("DEDALUS_AS_URL", "https://as.dedaluslabs.ai")
SEGMENT_API_KEY = os.getenv("SEGMENT_API_KEY", "")
MCP_SERVER_SLUG = os.getenv("MCP_SERVER_SLUG", "JiayuWang/segment-mcp")
MODEL           = os.getenv("DEDALUS_TEST_MODEL", "anthropic/claude-sonnet-4-5")

REQUIRED_TOOLS = ["segment_list_workspaces", "segment_list_sources", "segment_list_destinations", "segment_get_source_schema", "segment_create_tracking_plan", "segment_list_audiences"]


def _passed(tool_name: str, tool_events: list) -> bool:
    if not tool_events:
        return False
    for event in tool_events:
        if hasattr(event, "name") and tool_name in event.name:
            return True
        if isinstance(event, dict) and tool_name in event.get("name", ""):
            return True
    return False


async def _run_tool(runner, creds, tool_name: str, instruction: str) -> bool:
    print(f"\n--- {tool_name} ---")
    tool_events = []

    def on_tool_event(event):
        tool_events.append(event)

    try:
        result = await runner.run(
            input=instruction,
            model=MODEL,
            mcp_servers=[MCP_SERVER_SLUG],
            credentials=creds,
            max_steps=4,
            max_tokens=2000,
            on_tool_event=on_tool_event,
        )
        output = getattr(result, "output", str(result)) or ""
        print(output[:400])
        ok = _passed(tool_name, tool_events)
        if ok:
            print(f"✓ Tool called: {len(tool_events)} invocation(s)")
    except Exception as exc:
        print(f"exception: {exc!r}")
        ok = False
    print(f"[{'PASS' if ok else 'FAIL'}] {tool_name}")
    return ok


async def main() -> int:
    if not DEDALUS_API_KEY:
        print("Error: DEDALUS_API_KEY not set"); return 1
    if not SEGMENT_API_KEY:
        print("Error: SEGMENT_API_KEY not set"); return 1
    from dedalus_labs import AsyncDedalus, DedalusRunner
    from dedalus_mcp.auth import SecretValues

    creds = [SecretValues(_rebind(segment, MCP_SERVER_SLUG), token=SEGMENT_API_KEY)]
    client = AsyncDedalus(api_key=DEDALUS_API_KEY, base_url=DEDALUS_API_URL, as_base_url=DEDALUS_AS_URL)
    runner = DedalusRunner(client)

    print(f"Testing Segment MCP server: {MCP_SERVER_SLUG}")
    print("=" * 60)

    results: dict[str, bool] = {}

    results["segment_list_workspaces"] = await _run_tool(runner, creds, "segment_list_workspaces",
        "Call list_workspaces and show workspace ids.")
    results["segment_list_sources"] = await _run_tool(runner, creds, "segment_list_sources",
        "Call list_workspaces to get a workspace id, then call list_sources for it.")
    results["segment_list_destinations"] = await _run_tool(runner, creds, "segment_list_destinations",
        "Call list_workspaces to get a workspace id, then call list_destinations for it.")
    results["segment_get_source_schema"] = await _run_tool(runner, creds, "segment_get_source_schema",
        "Call list_workspaces, list_sources to get a source id, then call get_source_schema on it.")
    results["segment_list_audiences"] = await _run_tool(runner, creds, "segment_list_audiences",
        "Call list_workspaces to get a workspace id, then call list_audiences for it.")
    results["segment_create_tracking_plan"] = await _run_tool(runner, creds, "segment_create_tracking_plan",
        "Call list_workspaces to get a workspace id, then create_tracking_plan with name='Dedalus Smoke Test Plan'.")

    print("\n" + "=" * 60)
    print("Summary")
    for name in REQUIRED_TOOLS:
        ok = results.get(name, False)
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    all_pass = all(results.get(t, False) for t in REQUIRED_TOOLS)
    print("\nRESULT:", "ALL PASS" if all_pass else "SOME FAILED")
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
