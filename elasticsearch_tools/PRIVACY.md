## Privacy

This plugin interacts with your configured Elasticsearch clusters and processes the following data:
1. **Elasticsearch Authentication Information**  
    - The plugin relies on the platform to store and manage authentication information in the following format:  
      ```
      [{"<cluster_address>": "username:password"}]
      ```  
    - Here, the key of each object represents the cluster access address.  
    - The plugin only uses these credentials for API authentication and does not store or transmit them elsewhere.

2. **Elasticsearch Data**  
   - The plugin temporarily retrieves the following data from your Elasticsearch clusters:  
     - Cluster health status, indices, and other requested information  
   - Retrieved data is only used for temporary processing (e.g., displaying cluster health or performing requested operations) and is not permanently stored or shared with third parties by the plugin.

3. **API Communication**  
   - The plugin only communicates with your configured Elasticsearch clusters via API.  
   - All communication occurs directly between the plugin and your Elasticsearch clusters, without being routed through external services.  
   - The plugin does not send data to any external services.

### Data Protection

- The plugin itself does not store any data (including authentication information or cluster data).  
- All data processing is performed temporarily during plugin runtime, and no data is retained after processing.  
- The plugin does not include any analytics, tracking, or data-sharing functionality.  
- Authentication information is stored and managed by the platform it relies on, and the plugin only uses it for API authentication.

### Data Usage

The plugin only uses data for the following purposes:  
1. Retrieving authentication information from the platform to authenticate with your Elasticsearch clusters.  
2. Fetching cluster health status, indices, or other requested data.  
3. Performing operations on your Elasticsearch clusters as requested by the user.  
4. Returning processed results to the user.

For any questions regarding privacy, please contact the plugin author via GitHub: [https://github.com/stoplyy](https://github.com/stoplyy)