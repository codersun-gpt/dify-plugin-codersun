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
            address_list_text = credentials["address_list"]
            auth_list_text = credentials["auth_list"] # 格式 [{"101":"elastic:pwd"}]
            address_list = []
            auth_list = []
            # Convert string inputs to JSONArray

            try:
                address_list = json.loads(address_list_text)
            except json.JSONDecodeError:
                raise ToolProviderCredentialValidationError("address_list必须是有效的JSON数组格式")
                
            if auth_list_text:
                try:
                    auth_list = json.loads(auth_list_text)
                except json.JSONDecodeError:
                    raise ToolProviderCredentialValidationError("auth_list必须是有效的JSON数组格式")

            self._validate_input(address_list, auth_list)

            # check login
            failed_clusters = []
            for one_address in address_list:
                cluster_id = list(one_address.keys())[0]
                address = one_address[cluster_id]
                username = password = None
                
                # Convert auth_list to dict for easier lookup
                auth_dict = {}
                for auth_item in auth_list:
                    auth_dict.update(auth_item)
                
                if cluster_id in auth_dict:
                    username, password = auth_dict[cluster_id].split(":")

                helper = ElasticsearchHelper(address, username, password)

                try:
                    helper.cluster_health()
                except RequestException as e:
                    failed_clusters.append({
                        "cluster_id": cluster_id,
                        "error": str(e)
                    })

            if failed_clusters:
                error_msg = "以下集群验证失败:\n" + "\n".join(
                    [f"集群 {c['cluster_id']}: {c['error']}" for c in failed_clusters]
                )
                raise ToolProviderCredentialValidationError(error_msg)

        except ToolProviderCredentialValidationError as e:
            raise e
        except KeyError as e:
            raise ToolProviderCredentialValidationError(f"缺少必需的认证信息: {str(e)}") from e
        except Exception as e:
            raise ToolProviderCredentialValidationError(f"验证凭据时发生错误: {str(e)}") from e

    def _validate_input(self, address_list: list, auth_list: list) -> None:
        # Extract clusterIds from both lists  
        address_cluster_ids = {list(item.keys())[0] for item in address_list if isinstance(item, dict)}
        auth_cluster_ids = {list(item.keys())[0] for item in auth_list if isinstance(item, dict)}

        # Check if any clusterId is missing
        if not address_cluster_ids:
            raise ToolProviderCredentialValidationError("address_list中缺少clusterId")
        if auth_list and not auth_cluster_ids:
            raise ToolProviderCredentialValidationError("auth_list中缺少clusterId")
        
        # Check if auth_list is missing any required cluster IDs
        missing_in_address = auth_cluster_ids - address_cluster_ids
        if missing_in_address:
            error_msg = "address_list中缺少必需的clusterId: " + ", ".join(missing_in_address)
            raise ToolProviderCredentialValidationError(error_msg)
