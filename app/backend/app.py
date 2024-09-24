import os
from dotenv import load_dotenv
from aiohttp import web
from ragtools import attach_rag_tools
from rtmt import RTMiddleTier

if __name__ == "__main__":
    load_dotenv()
    llm_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    llm_key = os.environ.get("AZURE_OPENAI_API_KEY")
    search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
    search_index = os.environ.get("AZURE_SEARCH_INDEX")
    search_key = os.environ.get("AZURE_SEARCH_API_KEY")

    app = web.Application()

    rtmt = RTMiddleTier(llm_endpoint, llm_key)
    rtmt.system_message = "You are a helpful assistant. Respond with short and concise answers. Always use the 'search' " + \
                          "tool to check the knowledge base before answering a question. Always use the 'report_grounding' " + \
                          "tool to report the source of information from the knowledge base. " + \
                          "If the answer isn't in the knowledge base, say you don't know. "
    attach_rag_tools(rtmt, search_endpoint, search_index, search_key)

    rtmt.attach_to_app(app, "/realtime")

    app.add_routes([web.get('/', lambda _: web.FileResponse('./static/index.html'))])
    app.router.add_static('/', path='./static', name='static')
    web.run_app(app, host='localhost', port=8765)
