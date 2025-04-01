# Elasticsearch Tools Plugin

A Dify plugin for interacting with Elasticsearch clusters.

## Features

- Authenticate with Elasticsearch clusters using username and password
- Perform REST API calls to Elasticsearch clusters
- Support for various Elasticsearch operations:
  - Cluster health checks
  - Index management
  - Search queries
  - Custom REST API calls

## Available Tools

### 1. Elasticsearch REST API Tool
- Perform REST API calls to Elasticsearch clusters
- Support for GET, POST, PUT, and DELETE methods
- Flexible input for custom endpoints and request bodies
- Output results in various formats (object, array, or string)

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your Elasticsearch credentials in the plugin settings:
- Cluster Address: The address of your Elasticsearch cluster (e.g., `http://localhost:9200`)
- Username: Your Elasticsearch username
- Password: Your Elasticsearch password

## Usage

### Elasticsearch REST API Tool

1. Perform a REST API call:
   - Specify the cluster address, endpoint, method, and request body
   - Supports GET, POST, PUT, and DELETE methods

Parameters:
- `cluster_address`: The address of the Elasticsearch cluster (e.g., `http://localhost:9200`)
- `endpoint`: The API endpoint to call (e.g., `_cluster/health`)
- `method`: The HTTP method to use (`GET`, `POST`, `PUT`, or `DELETE`)
- `body`: The request body (optional, for POST and PUT methods)

Outputs:
- `success`: Indicates whether the API call was successful
- `result_object`: The response as an object (if applicable)
- `result_array`: The response as an array (if applicable)
- `result_string`: The response as a string (if applicable)

## Development

The plugin consists of these main components:

1. `ElasticsearchToolsTool`: Handles REST API calls to Elasticsearch
2. `ElasticsearchHelper`: Provides helper methods for interacting with Elasticsearch clusters
3. Credential validation and error handling logic

## Error Handling

The plugin handles various error scenarios:
- Authentication failures
- Invalid cluster addresses
- Network connection issues
- API response errors
- Missing parameters
- Invalid credentials

## Contributing

GitHub: [CoderSun](https://github.com/stoplyy)



