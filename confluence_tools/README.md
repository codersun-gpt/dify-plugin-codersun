# Confluence Tools Plugin

A Dify plugin for converting Confluence content to Markdown format.

## Features

- Authenticate with Confluence using username and password
- Fetch page content from Confluence using page ID
- Convert Confluence HTML content to Markdown format
- Support for various Confluence elements:
  - Headings (H1-H6)
  - Tables with rowspan and colspan
  - Code blocks with language syntax highlighting
  - Inline code
  - Paragraphs and line breaks
  - CDATA content handling

## Available Tools

### 1. HTML to Markdown Converter
- Convert Confluence page content to Markdown format
- Output as text or file
- Preserve formatting and structure

### 2. Page Content Fetcher
- Retrieve raw HTML content from Confluence pages
- Get page title and content
- Validate authentication
- Handle API errors gracefully

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your Confluence credentials in the plugin settings:
- Base URL: Your Confluence instance URL
- Username: Your Confluence username
- Password: Your Confluence password

## Usage

### HTML to Markdown Tool

1. Convert to Text:
   - Returns the Markdown content as text

2. Convert to File:
   - Saves the Markdown content as a .md file
   - Preserves the original page title as filename

Parameters:
- `pageId`: The Confluence page ID to convert
- `result_type`: Output format (`"text"` or `"file"`)

### Page Content Tool

Fetches raw content from a Confluence page:
- Returns page title and HTML content
- Validates credentials before fetching
- Provides detailed error messages

Parameters:
- `pageId`: The Confluence page ID to fetch

## Development

The plugin consists of these main components:

1. `HtmlMdTool`: Converts HTML content to Markdown
2. `PageContentTool`: Fetches raw page content
3. `ConfluenceHTMLParser`: HTML parser for converting content
4. Helper functions for API interactions

## Error Handling

The plugin handles various error scenarios:
- Authentication failures
- Invalid page IDs
- Network connection issues
- API response errors
- Missing parameters
- Invalid credentials

## Contributing

GitHub: [CoderSun](https://github.com/stoplyy)





