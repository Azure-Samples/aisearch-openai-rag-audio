import logging
import os
from pathlib import Path

from aiohttp import web
from azure.core.credentials import AzureKeyCredential
from azure.identity import AzureDeveloperCliCredential, DefaultAzureCredential
from dotenv import load_dotenv

from ragtools import attach_rag_tools
from rtmt import RTMiddleTier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("voicerag")

async def create_app():
    if not os.environ.get("RUNNING_IN_PRODUCTION"):
        logger.info("Running in development mode, loading from .env file")
        load_dotenv()

    llm_key = os.environ.get("AZURE_OPENAI_API_KEY")
    search_key = os.environ.get("AZURE_SEARCH_API_KEY")

    credential = None
    if not llm_key or not search_key:
        if tenant_id := os.environ.get("AZURE_TENANT_ID"):
            logger.info("Using AzureDeveloperCliCredential with tenant_id %s", tenant_id)
            credential = AzureDeveloperCliCredential(tenant_id=tenant_id, process_timeout=60)
        else:
            logger.info("Using DefaultAzureCredential")
            credential = DefaultAzureCredential()
    llm_credential = AzureKeyCredential(llm_key) if llm_key else credential
    search_credential = AzureKeyCredential(search_key) if search_key else credential
    
    app = web.Application()

    rtmt = RTMiddleTier(
        credentials=llm_credential,
        endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        deployment=os.environ["AZURE_OPENAI_REALTIME_DEPLOYMENT"],
        voice_choice=os.environ.get("AZURE_OPENAI_REALTIME_VOICE_CHOICE") or "alloy"
        )
    rtmt.system_message = """
You are an order-taking assistant at Circles Restaurant.
Always speak in Egyptian Arabic dialect (Masry ‘Aamiya) with a warm and friendly tone.
Keep responses short and focused.

Important rules:

Only answer questions based on information you searched in the knowledge base, accessible with the 'search' tool.

The user is listening to answers with audio, so it's super important that answers are as short as possible, a single sentence if at all possible.

Never switch to English.

Never speak in formal Arabic (Fusha).

Never give long sentences.

Stick strictly to the categories and rules below.

Never read file names, source names, or keys out loud.

If an item is not in the menu → say: "ليس عندي."

If you don’t understand → say: "ممكن توضّح أكتر يا فندم؟"

Always follow these step-by-step instructions when responding:

Always use the 'search' tool to check the knowledge base before answering a question.

Always follow the dialogue flow rules for ordering (see below).

Produce an answer that is as short as possible, one sentence if possible.

If the item or request is not in the menu, respond politely with "ليس عندي."

If the request is unclear, ask for clarification with "ممكن توضّح أكتر يا فندم؟"

Dialogue flow rules:

Opening line (always start with):
"مساء النور يا فندم في مطعم سيركلز.. إزيّك؟ تحب تطلب إيه؟"

Categories: Pizza, Burgers, Other Food, Drinks.

Pizza ordering:

Always ask for size (small, medium, large).

Example: "تحبها حجم إيه؟"

All other items (Burgers, Other Food, Drinks):

Only one size available.

Do not ask about size.

After each order:

Say: "تحب تزود حاجة تانية؟"

If yes → say: "تحب تزود إيه؟"

If no → calculate the total and say:
"الحساب [amount] جنيه.. والأوردر هيكون جاهز بعد نص ساعة."
    """.strip()

    attach_rag_tools(rtmt,
        credentials=search_credential,
        search_endpoint=os.environ.get("AZURE_SEARCH_ENDPOINT"),
        search_index=os.environ.get("AZURE_SEARCH_INDEX"),
        semantic_configuration=os.environ.get("AZURE_SEARCH_SEMANTIC_CONFIGURATION") or None,
        identifier_field=os.environ.get("AZURE_SEARCH_IDENTIFIER_FIELD") or "chunk_id",
        content_field=os.environ.get("AZURE_SEARCH_CONTENT_FIELD") or "chunk",
        embedding_field=os.environ.get("AZURE_SEARCH_EMBEDDING_FIELD") or "text_vector",
        title_field=os.environ.get("AZURE_SEARCH_TITLE_FIELD") or "title",
        use_vector_query=(os.getenv("AZURE_SEARCH_USE_VECTOR_QUERY", "true") == "true")
        )

    rtmt.attach_to_app(app, "/realtime")

    current_directory = Path(__file__).parent
    app.add_routes([web.get('/', lambda _: web.FileResponse(current_directory / 'static/index.html'))])
    app.router.add_static('/', path=current_directory / 'static', name='static')
    # إضافة route منفصل للملفات الصوتية
    app.router.add_static('/audio', path=current_directory / 'static/audio', name='audio')
    
    return app

if __name__ == "__main__":
    host = "localhost"
    port = 8765
    web.run_app(create_app(), host=host, port=port)
