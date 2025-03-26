## Privacy

This plugin interacts with your configured Confluence instance and processes the following data:

1. **Confluence Authentication Information**  
   - The plugin relies on the platform to store and manage the following authentication information:  
     - Base URL of your Confluence instance  
     - Username and password or API token for authentication  
   - The plugin only uses these credentials for API authentication and does not store or transmit them elsewhere.

2. **Confluence Page Content**  
   - The plugin temporarily retrieves the following data for requested pages:  
     - Page ID, title, and content  
   - Page content is only used for temporary processing (e.g., HTML to Markdown conversion) and is not permanently stored or shared with third parties by the plugin.

3. **API Communication**  
   - The plugin only communicates with your configured Confluence instance via API.  
   - All communication occurs directly between the plugin and your Confluence server, without being routed through external services.  
   - The plugin does not send data to any external services.

### Data Protection

- The plugin itself does not store any data (including authentication information or page content).  
- All data processing is performed temporarily during plugin runtime, and no data is retained after processing.  
- The plugin does not include any analytics, tracking, or data-sharing functionality.  
- Authentication information is stored and managed by the platform it relies on, and the plugin only uses it for API authentication.

### Data Usage

The plugin only uses data for the following purposes:  
1. Retrieving authentication information from the platform to authenticate with your Confluence instance.  
2. Fetching the content of requested pages.  
3. Converting content from HTML to Markdown format.  
4. Returning processed results to the user.

For any questions regarding privacy, please contact the plugin author via GitHub: [https://github.com/stoplyy](https://github.com/stoplyy)  
