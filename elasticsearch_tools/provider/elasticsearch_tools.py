"""Elasticsearch tools provider for Dify plugin."""

from typing import Any, Dict
from requests import RequestException
import json

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from helper.elasticsearch_helper import ElasticsearchHelper

class ElasticsearchToolsProvider(ToolProvider):
    """Provider for Elasticsearch API integration and credential validation."""
    
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            # Extract required credentials
            auth_list_text = credentials["auth_list"]  # 格式 [{"cluster_address":"username:password"}]
            auth_list = []

            # Convert string inputs to JSON array
            try:
                auth_list = json.loads(auth_list_text)
            except json.JSONDecodeError:
                raise ToolProviderCredentialValidationError("auth_list必须是有效的JSON数组格式")

            self._validate_input(auth_list)

            # Check login for each cluster
            failed_clusters = []
            for auth_item in auth_list:
                cluster_address = auth_item.get("cluster_address")
                if not cluster_address:
                    raise ToolProviderCredentialValidationError("auth_list中缺少cluster_address字段")

                try:
                    username, password = cluster_address.split(":")
                except ValueError:
                    raise ToolProviderCredentialValidationError(
                        f"cluster_address格式错误: {cluster_address}, 应为 'username:password'"
                    )

                helper = ElasticsearchHelper(cluster_address, username, password)

                try:
                    helper.cluster_health()
                except RequestException as e:
                    failed_clusters.append({
                        "cluster_address": cluster_address,
                        "error": str(e)
                    })

            if failed_clusters:
                error_msg = "以下集群验证失败:\n" + "\n".join(
                    [f"集群地址 {c['cluster_address']}: {c['error']}" for c in failed_clusters]
                )
                raise ToolProviderCredentialValidationError(error_msg)

        except ToolProviderCredentialValidationError as e:
            raise e
        except KeyError as e:
            raise ToolProviderCredentialValidationError(f"缺少必需的认证信息: {str(e)}") from e
        except Exception as e:
            raise ToolProviderCredentialValidationError(f"验证凭据时发生错误: {str(e)}") from e

    def _validate_input(self, auth_list: list) -> None:
        # Ensure auth_list contains valid cluster_address entries
        if not auth_list:
            raise ToolProviderCredentialValidationError("auth_list不能为空")

        for auth_item in auth_list:
            if not isinstance(auth_item, dict) or "cluster_address" not in auth_item:
                raise ToolProviderCredentialValidationError("auth_list中的每个项必须包含cluster_address字段")
