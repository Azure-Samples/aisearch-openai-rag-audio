from typing import Any, Optional
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchClient
from azure.search.documents.models import VectorizableTextQuery
from rtmt import RTMiddleTier, Tool, ToolResult, ToolResultDirection

_search_tool_schema = {
    "type": "function",
    "name": "search",
    "description": "Search the knowledge base. The knowledge base is in English, translate to and from Engligh if " + \
                    "needed. Results are formatted as a source name first in square brackets, followed by the text " + \
                    "content, and a line with '-----' at the end of each result.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query"
            }
        },
        "required": ["query"],
        "additionalProperties": False
    }
}

_grounding_tool_schema = {
    "type": "function",
    "name": "report_grounding",
    "description": "Report use of a source from the knowledge base as part of an answer",
    "parameters": {
        "type": "object",
        "properties": {
            "sources": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "List of source names from last statement actually used, do not include the ones not used to formulate a response"
            }
        },
        "required": ["sources"],
        "additionalProperties": False
    }
}

async def _search_tool(search_client: SearchClient, args: Any) -> ToolResult:
    print(f"Searching for '{args['query']}' in the knowledge base.")
    # Hybrid + Reranking query using Azure AI Search
    search_results = await search_client.search(
        search_text=args['query'], 
        query_type="semantic",
        top=3,
        vector_queries=[VectorizableTextQuery(text=args['query'], k_nearest_neighbors=50, fields="text_vector")])
    result = ""
    async for r in search_results:
        result += f"[{r['title']}]: {r['chunk']}\n-----\n"
    return ToolResult(result, ToolResultDirection.TO_SERVER)

async def _report_grounding_tool(args: Any) -> None:
    list = ",".join(args["sources"])
    print(f"Grounding source: {list}")
    return ToolResult(f"***grounding:{list}", ToolResultDirection.TO_CLIENT)

def attach_rag_tools(rtmt: RTMiddleTier, search_endpoint: str, search_index: str, search_key: Optional[str]) -> None:
    if search_key is None:
        search_creds = DefaultAzureCredential() 
        search_creds.get_token("https://search.azure.com/.default") # warm this up before we start getting requests
    else:
        search_creds = AzureKeyCredential(search_key)
    search_client = SearchClient(search_endpoint, search_index, search_creds)

    rtmt.tools["search"] = Tool(schema=_search_tool_schema, target=lambda q: _search_tool(search_client, q))
    rtmt.tools["report_grounding"] = Tool(schema=_grounding_tool_schema, target=_report_grounding_tool)
