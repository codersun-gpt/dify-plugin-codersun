from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from unit.confluence_session import ConfluenceSession


class PageContentTool(Tool):
    """Tool for fetching raw content from Confluence pages."""
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # Get parameters
        page_id = tool_parameters.get("pageId")
        if not page_id:
            yield self.create_text_message(text="Page ID is required")
            return

        # Get credentials
        base_url = self.runtime.credentials.get('baseUrl')
        username = self.runtime.credentials.get('userName')
        password = self.runtime.credentials.get('password')

        if not all([base_url, username, password]):
            yield self.create_text_message(text="Missing required credentials")
            return

        # Initialize session and fetch content
        session = ConfluenceSession(base_url, username, password)
        result = session.get_page_content(str(page_id))
        
        # Return single JSON response with success/failure info
        if not result["success"]:
            yield self.create_json_message({
                "success": False,
                "content": result["message"],
                "title": result.get("title", "获取文档异常！")
            })
            return

        yield self.create_json_message({
            "success": True,
            "title": result["title"],
            "content": result["results"]
        })