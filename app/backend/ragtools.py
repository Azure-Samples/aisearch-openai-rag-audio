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
    "description": "البحث في قاعدة المعرفة. قاعدة المعرفة باللغة العربية، ابحث مباشرة بالعربية. " + \
                   "النتائج تظهر كـ: [ID] اسم المنتج - المكونات (السعر جنيه)",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "استعلام البحث باللغة العربية"
            }
        },
        "required": ["query"],
        "additionalProperties": False
    }
}

_grounding_tool_schema = {
    "type": "function",
    "name": "report_grounding",
    "description": "الإبلاغ عن استخدام مصدر من قاعدة المعرفة كجزء من الإجابة (في الواقع، اقتباس المصدر).",
    "parameters": {
        "type": "object",
        "properties": {
            "sources": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "قائمة بأسماء المصادر من البيان الأخير المستخدم فعلاً"
            }
        },
        "required": ["sources"],
        "additionalProperties": False
    }
}

_show_all_tool_schema = {
    "type": "function", 
    "name": "show_all_items",
    "description": "عرض جميع المنتجات المتاحة في المطعم عندما يطلب العميل رؤية كل المنتجات أو القائمة الكاملة",
    "parameters": {
        "type": "object",
        "properties": {},
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
    
    query = args["query"]
    print(f"البحث عن '{query}' في قاعدة المعرفة العربية")
    print(f"استخدام الحقول: ID={identifier_field}, Content={content_field}")
    
    # بحث نصي بسيط في Azure AI Search مع دعم النص العربي
    search_results = await search_client.search(
        search_text=query, 
        query_type="simple",  # البحث النصي البسيط يدعم العربية جيداً
        top=5,
        select=f"{identifier_field},Name,{content_field},Price",
        search_mode="any"  # البحث عن أي كلمة من الكلمات المدخلة
    )
    
    result = ""
    result_count = 0
    async for r in search_results:
        result_count += 1
        print(f"نتيجة البحث {result_count}: {r}")
        
        # استخدام الحقول الصحيحة
        id_field = r.get(identifier_field, f"Item_{result_count}")
        name_field = r.get('Name', "منتج غير معروف")
        content_field_value = r.get(content_field, "بدون وصف")
        price = r.get('Price', 'سعر غير محدد')
        
        # عرض النتائج بصيغة عربية واضحة
        result += f"🍽️ [{id_field}] {name_field}\n"
        result += f"المكونات: {content_field_value}\n"
        result += f"السعر: {price} جنيه\n-----\n"
    
    if result_count == 0:
        print("لم توجد نتائج للبحث!")
        # إضافة اقتراحات إذا لم توجد نتائج
        result = "عذراً، لم أجد هذا المنتج. جرب البحث عن:\n"
        result += "🍕 بيتزا (فراخ، سي فود، كابوريا)\n"
        result += "🍔 برجر (بيف، دجاج، تشيزي)\n"
        result += "أو قل 'اعرض كل المنتجات'"
    else:
        print(f"وجدت {result_count} نتائج")
    
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

async def _show_all_tool(search_client: SearchClient, identifier_field: str, content_field: str) -> ToolResult:
    print("عرض جميع المنتجات المتاحة")
    
    # البحث عن جميع المنتجات
    search_results = await search_client.search(
        search_text="*", 
        query_type="simple",
        top=50,  # عرض حتى 50 منتج
        select=f"{identifier_field},Name,{content_field},Price",
        order_by=["Name"]  # ترتيب حسب الاسم
    )
    
    result = "🍽️ **قائمة المطعم الكاملة** 🍽️\n\n"
    result_count = 0
    
    # تجميع المنتجات حسب النوع
    pizzas = []
    burgers = []
    others = []
    
    async for r in search_results:
        result_count += 1
        
        id_field = r.get(identifier_field, f"Item_{result_count}")
        name_field = r.get('Name', "منتج غير معروف")
        content_field_value = r.get(content_field, "بدون وصف")
        price = r.get('Price', 'غير محدد')
        
        item_info = f"[{id_field}] {name_field} - {price} جنيه"
        
        if "بيتزا" in name_field:
            pizzas.append(item_info)
        elif "برجر" in name_field:
            burgers.append(item_info)
        else:
            others.append(item_info)
    
    if pizzas:
        result += "🍕 **البيتزا:**\n"
        for pizza in pizzas:
            result += f"   {pizza}\n"
        result += "\n"
    
    if burgers:
        result += "🍔 **البرجر:**\n" 
        for burger in burgers:
            result += f"   {burger}\n"
        result += "\n"
            
    if others:
        result += "🍽️ **منتجات أخرى:**\n"
        for other in others:
            result += f"   {other}\n"
        result += "\n"
    
    result += f"📊 إجمالي المنتجات: {result_count}\n"
    result += "قل اسم أي منتج للحصول على تفاصيل أكثر!"
    
    return ToolResult(result, ToolResultDirection.TO_SERVER)

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
    rtmt.tools["show_all_items"] = Tool(schema=_show_all_tool_schema, target=lambda args: _show_all_tool(search_client, identifier_field, content_field))
