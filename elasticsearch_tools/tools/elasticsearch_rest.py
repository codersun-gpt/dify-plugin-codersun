from collections.abc import Generator
from typing import Any
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from helper.elasticsearch_helper import ElasticsearchHelper

class ElasticsearchToolsTool(Tool):
    
    def output_variable_message(self, variable_name: str, variable_value: Any):
        return ToolInvokeMessage(
            variable_name=variable_name,
            variable_value=variable_value
        )
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        cluster_address = tool_parameters.get("cluster_address")  
        endpoint = tool_parameters.get("endpoint")
        method = tool_parameters.get("method")
        body = tool_parameters.get("body")

        auth_list_text = self.runtime.credentials["auth_list"]

        if not auth_list_text:
            auth_list = []
        else:
            auth_list = json.loads(auth_list_text)

        username = None
        password = None

        for item in auth_list:
            if item.get("cluster_address") == cluster_address:
                try:
                    username, password = cluster_address.split(":")
                except ValueError:
                    yield self.create_variable_message("success", False)
                    yield self.create_variable_message("error_message", f"cluster_address format error: {cluster_address}")
                    return
                break

        if not username or not password:
            yield self.create_variable_message("success", False)
            yield self.create_variable_message("error_message", f"Matching cluster_address not found: {cluster_address}")
            return

        helper = ElasticsearchHelper(cluster_address, username, password)
        result = helper._make_request(method, endpoint, json=body)

        yield self.create_variable_message("success", True)
        if isinstance(result, dict):
            yield self.create_variable_message("result_object", result)
        elif isinstance(result, list):
            yield self.create_variable_message("result_array", result)
        else:
            yield self.create_variable_message("result_string", str(result))