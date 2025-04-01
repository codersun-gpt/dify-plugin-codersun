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
        cluster_id = tool_parameters.get("cluster_id")
        endpoint = tool_parameters.get("endpoint")
        method = tool_parameters.get("method")
        body = tool_parameters.get("body")

        address_list_text = self.runtime.credentials["address_list"]
        auth_list_text = self.runtime.credentials["auth_list"]

        address_list = json.loads(address_list_text)
        if not auth_list_text:
            auth_list = []
        else:
            auth_list = json.loads(auth_list_text)

        address = None
        username = None
        password = None
        # 格式 address_list: [{"101":"http://127.0.0.1:9200"}]
        for item in address_list:
            if str(cluster_id) in item.keys():
                address = item[str(cluster_id)]
                break

        if not address:
            yield self.create_variable_message("success", False)
            yield self.create_variable_message("error_message", f"集群ID错误: {cluster_id} allIds: {address_list.keys()}")
            return
        
        for item in auth_list:
            if str(cluster_id) in item.keys():
                username, password = item[cluster_id].split(":")
                break

        helper = ElasticsearchHelper(address, username, password)
        result = helper._make_request(method, endpoint, json=body)

        yield self.create_variable_message("success", True)
        if isinstance(result, dict):
            yield self.create_variable_message("result_object", result)
        elif isinstance(result, list):
            yield self.create_variable_message("result_array", result)
        else:
            yield self.create_variable_message("result_string", str(result))