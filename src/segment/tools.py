"""Segment MCP tools - Type 3 DAuth implementation."""

import json
from typing import Optional

from mcp.types import TextContent
from dedalus_mcp import HttpMethod, HttpRequest, get_context, tool
from dedalus_mcp.auth import Connection, SecretKeys
from dedalus_mcp.types import ToolAnnotations

_BASE_URL = "https://api.segmentapis.com"

segment = Connection(
    name="JiayuWang-segment-mcp",
    secrets=SecretKeys(token="SEGMENT_API_KEY"),
    base_url=_BASE_URL,
    auth_header_format="Bearer {api_key}",
)

Result = list[TextContent]


async def _req(method: HttpMethod, path: str, body: dict | None = None, params: dict | None = None) -> Result:
    ctx = get_context()
    resp = await ctx.dispatch(
        "JiayuWang-segment-mcp",
        HttpRequest(method=method, path=path, body=body, params=params),
    )
    if resp.success:
        return [TextContent(type="text", text=json.dumps(resp.response.body or {}, indent=2))]
    error = resp.error.message if resp.error else "Request failed"
    return [TextContent(type="text", text=json.dumps({"error": error}, indent=2))]


@tool(description="Segment: list all workspaces", annotations=ToolAnnotations(readOnlyHint=True))
async def segment_list_workspaces() -> Result:
    return await _req(HttpMethod.GET, "/workspaces")


@tool(description="Segment: list all sources in a workspace", annotations=ToolAnnotations(readOnlyHint=True))
async def segment_list_sources(workspace_id: str) -> Result:
    return await _req(HttpMethod.GET, f"/workspaces/{workspace_id}/sources")


@tool(description="Segment: list all destinations in a workspace", annotations=ToolAnnotations(readOnlyHint=True))
async def segment_list_destinations(workspace_id: str) -> Result:
    return await _req(HttpMethod.GET, f"/workspaces/{workspace_id}/destinations")


@tool(description="Segment: get tracking schema for a source", annotations=ToolAnnotations(readOnlyHint=True))
async def segment_get_source_schema(source_id: str) -> Result:
    return await _req(HttpMethod.GET, f"/sources/{source_id}/schema")


@tool(description="Segment: create a tracking plan", annotations=ToolAnnotations(readOnlyHint=False))
async def segment_create_tracking_plan(workspace_id: str, name: str, description: Optional[str] = None) -> Result:
    body = {"name": name}
    if description:
        body["description"] = description
    return await _req(HttpMethod.POST, f"/workspaces/{workspace_id}/tracking-plans", body=body)


@tool(description="Segment: list audiences in a workspace", annotations=ToolAnnotations(readOnlyHint=True))
async def segment_list_audiences(workspace_id: str) -> Result:
    return await _req(HttpMethod.GET, f"/workspaces/{workspace_id}/audiences")


segment_tools = [
    segment_list_workspaces,
    segment_list_sources,
    segment_list_destinations,
    segment_get_source_schema,
    segment_create_tracking_plan,
    segment_list_audiences,
]

__all__ = ["segment", "segment_tools"]
