import re
from typing import Any

from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.search.documents.aio import SearchClient
from azure.search.documents.models import VectorizableTextQuery

from rtmt import RTMiddleTier, Tool, ToolResult, ToolResultDirection

_sumarize_conversation_tool = {
    "type": "function",
    "name": "sumarize_conversation",
    "description": "Summarizes the conversation you had with the user. Write a summary of " + \
        "the conversation in a concise manner, focusing on the key points discussed, " + \
        "and provide it as a single string so it can be sent to a support agent.",
    "parameters": {
        "type": "object",
        "properties": {
            "conversation_summary": {
                "type": "string",
                "description": "The sumarized conversation"
            }
        },
        "required": ["conversation_summary"],
        "additionalProperties": False
    }
}

async def _sumarize_conversation(conversation: dict) -> ToolResult:
    """
    Summarizes the conversation.
    """
    print(f'conversation: {conversation}')
    conversation_summary = conversation['conversation_summary']
    
    conversation_summary = re.sub(r'http[s]?://\S+', '', conversation_summary)
    
    summary = f"Summary of the conversation: {conversation_summary}..."  # Truncate for brevity
    return ToolResult({"conversation_summary": summary}, ToolResultDirection.TO_CLIENT)

def attach_sumarization_tools(rtmt: RTMiddleTier) -> None:
    """
    Attach sumarization tools to the RTMiddleTier instance.
    """
    rtmt.tools["sumarize_conversation"] = Tool(
        schema=_sumarize_conversation_tool,
        target=lambda args: _sumarize_conversation(args)
    )