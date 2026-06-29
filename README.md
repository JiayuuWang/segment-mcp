# Segment MCP Server

Type 3 DAuth MCP server for the [Segment](https://segment.com) API.

## Tools

| Tool | Description |
|------|-------------|
| `list_workspaces` | List Workspaces |
| `list_sources` | List Sources |
| `list_destinations` | List Destinations |
| `get_source_schema` | Get Source Schema |
| `create_tracking_plan` | Create Tracking Plan |
| `list_audiences` | List Audiences |

## Auth Setup (Public API key (Bearer))

1. Go to **Segment → Settings → Access Management → Tokens**
2. Create a workspace token with read access

## Environment Variables

```bash
SEGMENT_API_KEY=your_token
```

## Deploy

```bash
pip install -e .
python src/main.py
```

## Usage

```python
result = await runner.run(
    input="Show me segment data",
    mcp_servers=["JiayuWang/segment-mcp"],
)
```

## Safety Notes

- All read tools are safe for production
- Write tools are clearly marked with ⚠️ in their descriptions
