import io
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from unit.confluence_html_parser import ConfluenceHTMLParser
from unit.confluence_session import ConfluenceSession


class HtmlMdTool(Tool):
    """Tool for converting Confluence HTML content to Markdown format."""
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # Get required parameters
        page_id = tool_parameters.get("pageId")
        base_url = self.runtime.credentials['baseUrl']
        username = self.runtime.credentials['userName']
        password = self.runtime.credentials['password']
        result_type = tool_parameters.get("result_type")
        add_level_mark = tool_parameters.get("add_level_mark", False)
        mark_prefix = tool_parameters.get("mark_prefix", "L_")
        
        # Validate required parameters
        if not all([base_url, page_id, username, password]):
            yield self.create_text_message(text="参数错误")
            return

        # Initialize session and get page content
        session = ConfluenceSession(base_url, username, password)
        wiki = session.get_page_content(page_id)

        if not wiki.get('success'):
            yield self.create_text_message(text=wiki.get('message', '未知错误'))
            return

        wiki_content = wiki.get('results', '')
        wiki_title = wiki.get('title', 'untitled')

        print(f'success get wiki content: {wiki_title} length: {len(wiki_content)}')

        # Convert HTML to Markdown
        parser = ConfluenceHTMLParser(add_level_mark=add_level_mark, mark_prefix=mark_prefix)
        parser.feed(wiki_content)
        markdown_output = parser.get_markdown()
        print(f'success convert wiki content to markdown: {wiki_title}')

        # Return result based on requested type
        if result_type == 'file':
            buffer = io.BytesIO()
            buffer.write(markdown_output.encode('utf-8'))
            buffer.seek(0)
            yield self.create_blob_message(
                blob=buffer.getvalue(),
                meta={
                    'mime_type': 'text/markdown',
                    'filename': f"{wiki_title}.md",
                    'original_filename': wiki_title,
                    'save_as': f"{wiki_title}.md",
                },
            )
            return
        else:
            yield self.create_text_message(text=markdown_output)
            return
