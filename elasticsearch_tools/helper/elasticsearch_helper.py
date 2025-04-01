"""Helper class for Elasticsearch operations."""

from typing import Dict
import requests
from urllib.parse import urljoin


class ElasticsearchHelper:
    """Helper class for Elasticsearch HTTP operations."""
    
    def __init__(self, cluster_url: str, username: str, password: str):
        """Initialize ES helper with cluster credentials.
        
        Args:
            cluster_url: Elasticsearch cluster URL
            username: ES username
            password: ES password
        """
        self.base_url = cluster_url.rstrip('/')
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make HTTP request to ES cluster.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            **kwargs: Additional arguments for requests
            
        Returns:
            Response JSON data
            
        Raises:
            requests.RequestException: If request fails
        """
        url = urljoin(self.base_url, endpoint)
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()

    def cluster_health(self) -> Dict:
        """Get cluster health status."""
        return self._make_request('GET', '/_cluster/health')

    def cluster_info(self) -> Dict:
        """Get cluster information."""
        return self._make_request('GET', '/')
    
    def get_index_mapping(self, index: str) -> Dict:
        """Get index mapping."""
        return self._make_request('GET', f'/{index}/_mapping')
    
    def get_index_settings(self, index: str) -> Dict:
        """Get index settings."""
        return self._make_request('GET', f'/{index}/_settings')
    
    def get_index_stats(self, index: str) -> Dict:
        """Get index stats."""
        return self._make_request('GET', f'/{index}/_stats')
    
    def search(self, index: str, query: Dict) -> Dict:
        """Execute search query.
        
        Args:
            index: Index name
            query: Search query body
        """
        return self._make_request('POST', f'/{index}/_search', json=query)
    
    def write_to_index(self, index: str, doc: Dict) -> Dict:
        """Write document to index."""
        return self._make_request('POST', f'/{index}/_doc', json=doc)
    
    def delete_from_index(self, index: str, doc_id: str) -> Dict:
        """Delete document from index."""
        return self._make_request('DELETE', f'/{index}/_doc/{doc_id}')
    
    def update_document(self, index: str, doc_id: str, doc: Dict) -> Dict:
        """Update document in index."""
        return self._make_request('PUT', f'/{index}/_doc/{doc_id}', json=doc)
    
    def get_document(self, index: str, doc_id: str) -> Dict:
        """Get document from index."""
        return self._make_request('GET', f'/{index}/_doc/{doc_id}')