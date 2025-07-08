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
    "description": "Summarize the conversation you had with the user. Write a summary of " + \
        "the conversation in a concise manner, focusing on the key points discussed, " + \
        "and provide it as a single string so it can be sent to a support agent.",
    "parameters": {
        "type": "object",
        "properties": {
            "detected_issue": {
                "type": "string",
                "description": "The issue detected in the conversation. This should be a brief description of the user's issue or question."
            },
            "conversation_summary": {
                "type": "string",
                "description": "The sumarized conversation"
            },
            "appropriate_department": {
                "type": "string",
                "description": "The department that should handle the conversation, if applicable"
            },
            "detected_mood": {
                "type": "string",
                "description": "The detected mood of the user during the conversation"
            }, 
            "mood_level": {
                "type": "integer",
                "description": "The mood level of the user during the conversation, from 1 to 5"
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
    
    return ToolResult( conversation, ToolResultDirection.TO_CLIENT)

def attach_sumarization_tools(rtmt: RTMiddleTier) -> None:
    """
    Attach sumarization tools to the RTMiddleTier instance.
    """
    rtmt.tools["sumarize_conversation"] = Tool(
        schema=_sumarize_conversation_tool,
        target=lambda args: _sumarize_conversation(args)
    )