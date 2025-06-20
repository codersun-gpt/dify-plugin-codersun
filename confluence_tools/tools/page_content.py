from collections.abc import Generator
from typing import Any

import io
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
        result_type = tool_parameters.get("result_type")

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
        
        fileTitle = result["title"]
        content = result["results"]
        
        if result_type == 'file':
            buffer = io.BytesIO()
            buffer.write(content.encode('utf-8'))
            buffer.seek(0)
            yield self.create_blob_message(
                blob=buffer.getvalue(),
                meta={
                    'mime_type': 'text/markdown',
                    'filename': f"{fileTitle}",
                    'original_filename': fileTitle,
                    'save_as': f"{fileTitle}.md",
                },
            )
            return
        else:
            # Return content as JSON
            yield self.create_json_message({
                "success": True,
                "title": fileTitle,
                "content": content
            })