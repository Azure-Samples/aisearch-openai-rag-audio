import re
from typing import Any

from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.search.documents.aio import SearchClient
from azure.search.documents.models import VectorizableTextQuery

from rtmt import RTMiddleTier, Tool, ToolResult, ToolResultDirection

_search_tool_schema = {
    "type": "function",
    "name": "search",
    "description": "Search the knowledge base. The knowledge base is in English, translate to and from English if " + \
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
    "description": "Report use of a source from the knowledge base as part of an answer (effectively, cite the source). Sources " + \
                   "appear in square brackets before each knowledge base passage. Always use this tool to cite sources when responding " + \
                   "with information from the knowledge base.",
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

async def _search_tool(
    search_client: SearchClient, 
    semantic_configuration: str | None,
    identifier_field: str,
    content_field: str,
    embedding_field: str,
    use_vector_query: bool,
    args: Any) -> ToolResult:
    print(f"Searching for '{args['query']}' in the knowledge base.")
    print(f"Using fields: ID={identifier_field}, Content={content_field}")
    
    # Simple text search in Azure AI Search (no vector search, no semantic search)
    search_results = await search_client.search(
        search_text=args["query"], 
        query_type="simple",  # استخدام البحث النصي البسيط فقط
        top=5,
        select=f"{identifier_field},Name,{content_field},Price"  # تحديد الحقول المطلوبة
    )
    
    result = ""
    result_count = 0
    async for r in search_results:
        result_count += 1
        print(f"Search result {result_count}: {r}")  # طباعة النتيجة الكاملة
        
        # استخدام الحقول الصحيحة
        id_field = r.get(identifier_field, f"Item_{result_count}")
        name_field = r.get('Name', "Unknown Item")
        content_field_value = r.get(content_field, "No description available")
        price = r.get('Price', 'سعر غير محدد')
        
        # عرض النتائج بصيغة: [ID]: Name - ingredients (Price جنيه)
        result += f"[{id_field}]: {name_field} - {content_field_value} ({price} جنيه)\n-----\n"
    
    if result_count == 0:
        print("No search results found!")
        result = "ليس عندي."
    else:
        print(f"Found {result_count} results")
    
    return ToolResult(result, ToolResultDirection.TO_SERVER)

KEY_PATTERN = re.compile(r'^[a-zA-Z0-9_=\-]+$')

# TODO: move from sending all chunks used for grounding eagerly to only sending links to 
# the original content in storage, it'll be more efficient overall
async def _report_grounding_tool(search_client: SearchClient, identifier_field: str, title_field: str, content_field: str, args: Any) -> None:
    sources = [s for s in args["sources"] if KEY_PATTERN.match(s)]
    list = " OR ".join(sources)
    print(f"Grounding source: {list}")
    # Use search instead of filter to align with how the index is structured
    search_results = await search_client.search(search_text=list, 
                                                search_fields=[identifier_field], 
                                                select=[identifier_field, title_field, content_field], 
                                                top=len(sources), 
                                                query_type="full")
    
    docs = []
    async for r in search_results:
        docs.append({"ID": r[identifier_field], "Name": r[title_field], "ingredients": r[content_field]})
    return ToolResult({"sources": docs}, ToolResultDirection.TO_CLIENT)

def attach_rag_tools(rtmt: RTMiddleTier,
    credentials: AzureKeyCredential | DefaultAzureCredential,
    search_endpoint: str, search_index: str,
    semantic_configuration: str | None,
    identifier_field: str,
    content_field: str,
    embedding_field: str,
    title_field: str,
    use_vector_query: bool
    ) -> None:
    if not isinstance(credentials, AzureKeyCredential):
        credentials.get_token("https://search.azure.com/.default") # warm this up before we start getting requests
    search_client = SearchClient(search_endpoint, search_index, credentials, user_agent="RTMiddleTier")

    rtmt.tools["search"] = Tool(schema=_search_tool_schema, target=lambda args: _search_tool(search_client, semantic_configuration, identifier_field, content_field, embedding_field, use_vector_query, args))
    rtmt.tools["report_grounding"] = Tool(schema=_grounding_tool_schema, target=lambda args: _report_grounding_tool(search_client, identifier_field, title_field, content_field, args))
