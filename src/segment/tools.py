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


async def _req(
    method: HttpMethod,
    path: str,
    body: dict | None = None,
    params: dict | None = None,
) -> Result:
    ctx = get_context()
    resp = await ctx.dispatch(
        "JiayuWang-segment-mcp",
        HttpRequest(method=method, path=path, body=body, params=params),
    )
    if resp.success:
        data = resp.response.body or {}
        return [TextContent(type="text", text=json.dumps(data, indent=2))]
    error = resp.error.message if resp.error else "Request failed"
    return [TextContent(type="text", text=json.dumps({"error": error}, indent=2))]


@tool(
    description="List all workspaces in the Segment account",
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def list_workspaces() -> Result:
    """List all workspaces accessible by the API key."""
    return await _req(HttpMethod.GET, "/workspaces")


@tool(
    description="List all sources in a workspace",
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def list_sources(workspace_id: str) -> Result:
    """List all sources in the specified workspace."""
    return await _req(HttpMethod.GET, f"/workspaces/{workspace_id}/sources")


@tool(
    description="List all destinations in a workspace",
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def list_destinations(workspace_id: str) -> Result:
    """List all destinations configured in the workspace."""
    return await _req(HttpMethod.GET, f"/workspaces/{workspace_id}/destinations")


@tool(
    description="Get the schema (event structure) for a source",
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def get_source_schema(source_id: str) -> Result:
    """Get the tracking schema for a specific source."""
    return await _req(HttpMethod.GET, f"/sources/{source_id}/schema")


@tool(
    description="Create a new tracking plan to standardize event tracking",
    annotations=ToolAnnotations(readOnlyHint=False),
)
async def create_tracking_plan(
    workspace_id: str,
    name: str,
    description: Optional[str] = None,
) -> Result:
    """Create a tracking plan.
    
    Args:
        workspace_id: Target workspace
        name: Tracking plan name
        description: Optional description
    """
    body = {"name": name}
    if description:
        body["description"] = description
    return await _req(HttpMethod.POST, f"/workspaces/{workspace_id}/tracking-plans", body=body)


@tool(
    description="List audiences (user segments) in a workspace",
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def list_audiences(workspace_id: str) -> Result:
    """List all audiences configured in the workspace."""
    return await _req(HttpMethod.GET, f"/workspaces/{workspace_id}/audiences")


segment_tools = [
    list_workspaces,
    list_sources,
    list_destinations,
    get_source_schema,
    create_tracking_plan,
    list_audiences,
]

__all__ = ["segment", "segment_tools"]
