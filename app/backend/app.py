import os
from typing import Any, List
from dotenv import load_dotenv
from aiohttp import web
from rtmt import RTMiddleTier, Tool, ToolResult, ToolResultDirection
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchClient
from azure.search.documents.models import VectorizableTextQuery

search_tool_schema = {
    "type": "function",
    "function": {
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
        },
    }
}

grounding_tool_schema = {
    "type": "function",
    "function": {
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
        },
    }
}

async def search_tool(search_client: SearchClient, args: Any) -> ToolResult:
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

async def report_grounding_tool(args: Any) -> None:
    list = ",".join(args["sources"])
    print(f"Grounding source: {list}")
    return ToolResult(f"***grounding:{list}", ToolResultDirection.TO_CLIENT)

if __name__ == "__main__":
    load_dotenv()
    llm_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    key = os.environ.get("AZURE_OPENAI_API_KEY")
    search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
    search_index = os.environ.get("AZURE_SEARCH_INDEX")
    search_key = os.environ.get("AZURE_SEARCH_API_KEY")

    if search_key is None:
        search_creds = DefaultAzureCredential() 
        search_creds.get_token("https://search.azure.com/.default") # warm this up before we start getting requests
    else:
        search_creds = AzureKeyCredential(search_key)
    search_client = SearchClient(search_endpoint, search_index, search_creds)

    app = web.Application()

    rtmt = RTMiddleTier(llm_endpoint, key)
    rtmt.system_message = "You are a helpful assistant. Respond with short and concise answers. Always use the 'search' " + \
                          "tool to check the knowledge base before answering a question. Always use the 'report_grounding' " + \
                          "tool to report the source of information from the knowledge base. " + \
                          "If the answer isn't in the knowledge base, say you don't know. "
                        
    rtmt.tools["search"] = Tool(schema=search_tool_schema, target=lambda q: search_tool(search_client, q))
    rtmt.tools["report_grounding"] = Tool(schema=grounding_tool_schema, target=report_grounding_tool)
    rtmt.attach_to_app(app, "/realtime")

    app.add_routes([web.get('/', lambda _: web.FileResponse('./static/index.html'))])
    app.router.add_static('/', path='./static', name='static')
    web.run_app(app, host='localhost', port=8765)
