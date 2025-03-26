"""Module for managing Confluence API sessions and authentication."""

from typing import Dict, Any
import requests


class ConfluenceSession:
    """Manages Confluence API session and authentication."""

    def __init__(self, base_url: str, username: str, password: str):
        """Initialize Confluence session with credentials.
        
        Args:
            base_url: Base URL of the Confluence instance
            username: Confluence username
            password: Confluence password
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.headers = {'Content-Type': 'application/json'}

    @property
    def base_api_url(self) -> str:
        """Get the base API URL for Confluence."""
        return f"{self.base_url}/rest/api"

    def validate_credentials(self) -> Dict[str, Any]:
        """Validate the provided credentials by making a test API call.
        
        Returns:
            Dict containing success status and message
        """
        try:
            user_url = f"{self.base_api_url}/user/current"
            response = self.session.get(user_url, headers=self.headers)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "认证成功"
                }
            return {
                "success": False,
                "message": f"登录失败，错误代码: {response.status_code}",
                "details": response.text
            }
        except requests.RequestException as e:
            return {
                "success": False,
                "message": "认证请求失败",
                "details": str(e)
            }

    def get_page_content(self, page_id: str) -> Dict[str, Any]:
        """Fetch page content from Confluence.
        
        Args:
            page_id: ID of the Confluence page
            
        Returns:
            Dict containing page content, title, success status and message
        """
        # First validate credentials
        auth_result = self.validate_credentials()
        if not auth_result["success"]:
            return auth_result
            
        try:
            search_url = f"{self.base_api_url}/content/{page_id}?expand=body.storage"
            response = self.session.get(search_url, headers=self.headers)
            
            if response.status_code == 200:
                res_json = response.json()
                return {
                    "success": True,
                    "results": res_json['body']['storage']['value'],
                    "title": res_json['title'],
                    "message": "获取文档成功"
                }
            return {
                "success": False,
                "results": "",
                "title": "获取文档异常！",
                "message": f"获取文档异常！异常代码：{response.status_code}"
            }
        except requests.RequestException as e:
            return {
                "success": False,
                "message": f"请求失败 异常：{str(e)}"
            } 