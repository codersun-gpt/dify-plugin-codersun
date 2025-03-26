from typing import Any
import requests

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class ConfluenceToolsProvider(ToolProvider):
    """Provider for Confluence API integration and credential validation."""
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            # Extract required credentials
            base_url = credentials["baseUrl"]
            username = credentials["userName"]
            password = credentials["password"]

            # Setup session and headers
            session = requests.Session()
            session.auth = (username, password)
            headers = {'Content-Type': 'application/json'}

            # Make API request to validate credentials
            base_api_url = f"{base_url}/rest/api"
            response = session.get(
                f"{base_api_url}/user/current",
                headers=headers
            )

            if response.status_code != 200:
                raise ToolProviderCredentialValidationError(
                    f"Confluence登录失败，HTTP状态码: {response.status_code}，响应内容: {response.text}"
                )

        except KeyError as e:
            raise ToolProviderCredentialValidationError(f"缺少必需的认证信息: {str(e)}") from e
        except requests.RequestException as e:
            raise ToolProviderCredentialValidationError(f"请求Confluence API失败: {str(e)}") from e
        except Exception as e:
            raise ToolProviderCredentialValidationError(f"验证凭据时发生错误: {str(e)}") from e
