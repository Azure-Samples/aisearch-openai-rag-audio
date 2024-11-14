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
            logger.info(
                "Using AzureDeveloperCliCredential with tenant_id %s", tenant_id)
            credential = AzureDeveloperCliCredential(
                tenant_id=tenant_id, process_timeout=60)
        else:
            logger.info("Using DefaultAzureCredential")
            credential = DefaultAzureCredential()
    llm_credential = AzureKeyCredential(llm_key) if llm_key else credential
    search_credential = AzureKeyCredential(
        search_key) if search_key else credential

    app = web.Application()

    rtmt = RTMiddleTier(
        credentials=llm_credential,
        endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        deployment=os.environ["AZURE_OPENAI_REALTIME_DEPLOYMENT"],
        voice_choice=os.environ.get(
            "AZURE_OPENAI_REALTIME_VOICE_CHOICE") or "alloy"
    )
    rtmt.system_message = "You are a professional debt-collecting voice assistant agent representing StoneInk Corporation. When a user contacts you, your job is to politely collect their account details, inform them about their current payment status, and help them schedule their upcoming payments. " + \
        "The user is listening to answers with audio, so keep responses *super* short, polite, and to the point, ideally one sentence. " + \
        "Never disclose sensitive details like account numbers or personal information aloud unless explicitly required for confirmation. " + \
        "Below are examples of how to respond as a StoneInk Corporation debt-collecting agent: \n\n" + \
        "User: I want to know my payment status.\n" + \
        "Assistant: Can you please provide your account number or registered phone number to proceed?\n\n" + \
        "User: I think I missed my last payment. What do I do?\n" + \
        "Assistant: Let me confirm your account details first—can you provide your registered email or phone number?\n\n" + \
        "User: Can I pay next week instead?\n" + \
        "Assistant: Sure, I can help schedule that for you. What date works best?\n\n" + \
        "User: What’s my current balance?\n" + \
        "Assistant: Your balance is $250. Would you like to settle it now or schedule a payment?\n\n" + \
        "Always maintain a polite tone, confirm account details first, and offer payment options. If unsure or unable to retrieve specific information, politely inform the user and suggest contacting StoneInk customer service directly."
    attach_rag_tools(rtmt,
                     credentials=search_credential,
                     search_endpoint=os.environ.get("AZURE_SEARCH_ENDPOINT"),
                     search_index=os.environ.get("AZURE_SEARCH_INDEX"),
                     semantic_configuration=os.environ.get(
                         "AZURE_SEARCH_SEMANTIC_CONFIGURATION") or "default",
                     identifier_field=os.environ.get(
                         "AZURE_SEARCH_IDENTIFIER_FIELD") or "chunk_id",
                     content_field=os.environ.get(
                         "AZURE_SEARCH_CONTENT_FIELD") or "chunk",
                     embedding_field=os.environ.get(
                         "AZURE_SEARCH_EMBEDDING_FIELD") or "text_vector",
                     title_field=os.environ.get(
                         "AZURE_SEARCH_TITLE_FIELD") or "title",
                     use_vector_query=(os.environ.get(
                         "AZURE_SEARCH_USE_VECTOR_QUERY") == "true") or True
                     )

    # Add new /test route
    rtmt.attach_to_app(app, "/realtime")

    current_directory = Path(__file__).parent

    app.add_routes(
        [web.get('/', lambda _: web.FileResponse(current_directory / 'static/index.html'))])
    app.router.add_static('/', path=current_directory /
                          'static', name='static')
    app.router.add_get('/test', handle_test)

    return app

if __name__ == "__main__":
    host = "localhost"
    port = 8765
    web.run_app(create_app(), host=host, port=port)


async def handle_test(request):
    return web.json_response({"message": "Hi, backend running"})


async def save_debt_status(request):
    """API route to save the debt status to a JSON file."""
    try:
        data = await request.json()

        # Ensure the data directory exists
        DATA_DIR.mkdir(exist_ok=True)

        # Save the data to the JSON file
        with open(DEBT_STATUS_FILE, "w") as f:
            json.dump(data, f, indent=4)

        return web.json_response({"message": "Debt status saved successfully."})
    except Exception as e:
        logger.error(f"Failed to save debt status: {e}")
        return web.json_response({"message": "Failed to save debt status."}, status=500)
