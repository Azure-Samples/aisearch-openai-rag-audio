# 🔧 Technical Implementation Guide

## 🏗️ System Components Overview

### 🎤 Audio System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Audio Processing Layer                   │
├─────────────────────────────────────────────────────────────┤
│ Frontend Audio Manager                                      │
│ ├── Audio Sequence Player (3-stage playback)               │
│ ├── WebRTC Audio Recorder (real-time capture)              │
│ ├── Audio Worklet (low-latency processing)                 │
│ └── Audio Visualizer (real-time feedback)                  │
├─────────────────────────────────────────────────────────────┤
│ Backend Audio Handler                                       │
│ ├── Static File Server (audio assets)                      │
│ ├── WebSocket Audio Stream (real-time data)                │
│ └── Azure OpenAI Integration (speech processing)           │
└─────────────────────────────────────────────────────────────┘
```

### 🔍 RAG Processing Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                     RAG Integration Flow                    │
├─────────────────────────────────────────────────────────────┤
│ 1. Voice Input → Speech-to-Text (Azure OpenAI)             │
│ 2. Text Query → Arabic Processing (ragtools.py)            │
│ 3. Search Query → Azure AI Search (Arabic index)           │
│ 4. Results → Context Enhancement (smart formatting)        │
│ 5. Enhanced Context → GPT Response Generation              │
│ 6. Text Response → Speech Synthesis (Azure OpenAI)         │
│ 7. Audio Output → User Hearing Response                    │
└─────────────────────────────────────────────────────────────┘
```

## 🎵 Audio Sequence Implementation

### Frontend JavaScript/TypeScript

```typescript
// app/frontend/src/hooks/useAudioSequence.tsx
import { useState, useCallback } from 'react';

export interface AudioStage {
  file: string;
  duration: number;
  description: string;
}

const AUDIO_SEQUENCE: AudioStage[] = [
  { file: '/audio/Ran.mp3', duration: 3000, description: 'System initialization' },
  { file: '/audio/between.wav', duration: 1000, description: 'Transition' },
  { file: '/audio/Nancy.wav', duration: 2000, description: 'Welcome message' }
];

export const useAudioSequence = () => {
  const [currentStage, setCurrentStage] = useState<number>(-1);
  const [isPlaying, setIsPlaying] = useState(false);

  const playSequence = useCallback(async (): Promise<void> => {
    setIsPlaying(true);
    setCurrentStage(0);

    for (let i = 0; i < AUDIO_SEQUENCE.length; i++) {
      const stage = AUDIO_SEQUENCE[i];
      setCurrentStage(i);
      
      // Play audio file
      const audio = new Audio(stage.file);
      await new Promise<void>((resolve, reject) => {
        audio.onended = () => resolve();
        audio.onerror = reject;
        audio.play();
      });
      
      // Brief pause between stages
      await new Promise(resolve => setTimeout(resolve, 100));
    }

    setCurrentStage(-1);
    setIsPlaying(false);
  }, []);

  return {
    playSequence,
    currentStage,
    isPlaying,
    stageDescription: currentStage >= 0 ? AUDIO_SEQUENCE[currentStage]?.description : null
  };
};
```

### Audio Player Component

```typescript
// app/frontend/src/components/audio/AudioSequencePlayer.tsx
import React from 'react';
import { useAudioSequence } from '../../hooks/useAudioSequence';

interface AudioSequencePlayerProps {
  onSequenceComplete: () => void;
}

export const AudioSequencePlayer: React.FC<AudioSequencePlayerProps> = ({
  onSequenceComplete
}) => {
  const { playSequence, currentStage, isPlaying, stageDescription } = useAudioSequence();

  const handleStartSequence = async () => {
    await playSequence();
    onSequenceComplete();
  };

  return (
    <div className="audio-sequence-player">
      <button
        onClick={handleStartSequence}
        disabled={isPlaying}
        className={`sequence-button ${isPlaying ? 'playing' : 'ready'}`}
      >
        {isPlaying ? (
          <div className="playing-indicator">
            <span className="stage-number">{currentStage + 1}/3</span>
            <span className="stage-description">{stageDescription}</span>
          </div>
        ) : (
          'Start Voice Conversation'
        )}
      </button>
    </div>
  );
};
```

## 🔍 RAG Tools Implementation

### Core RAG Processing

```python
# app/backend/ragtools.py
import asyncio
from typing import Any, Dict, List
from azure.search.documents.aio import SearchClient
from azure.core.credentials import AzureKeyCredential

class ArabicRAGProcessor:
    def __init__(self, search_client: SearchClient):
        self.search_client = search_client
        
    async def search_arabic_content(self, query: str) -> List[Dict[str, Any]]:
        """
        Perform Arabic-optimized search in Azure AI Search
        """
        print(f"البحث عن '{query}' في قاعدة المعرفة العربية")
        
        # Configure search for Arabic language processing
        search_results = await self.search_client.search(
            search_text=query,
            query_type="simple",  # Best for Arabic text
            search_mode="any",    # Match any terms for flexibility
            top=5,
            select="ID,Name,ingredients,Price",
            highlight_fields=["Name", "ingredients"]
        )
        
        results = []
        async for result in search_results:
            enhanced_result = self._enhance_result_formatting(result)
            results.append(enhanced_result)
            
        return results
    
    def _enhance_result_formatting(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format search results for Arabic display
        """
        return {
            "id": result.get("ID", "غير محدد"),
            "name": result.get("Name", "منتج غير معروف"),
            "ingredients": result.get("ingredients", "مكونات غير متوفرة"),
            "price": f"{result.get('Price', 'غير محدد')} جنيه",
            "formatted_display": self._create_display_text(result)
        }
    
    def _create_display_text(self, result: Dict[str, Any]) -> str:
        """
        Create formatted text for voice response
        """
        name = result.get("Name", "منتج غير معروف")
        price = result.get("Price", "غير محدد")
        ingredients = result.get("ingredients", "مكونات غير متوفرة")
        
        return f"🍽️ {name}\nالمكونات: {ingredients}\nالسعر: {price} جنيه\n-----"

# RAG Tool Integration with Realtime API
async def _search_tool(
    search_client: SearchClient,
    semantic_configuration: str | None,
    identifier_field: str,
    content_field: str,
    embedding_field: str,
    use_vector_query: bool,
    args: Any
) -> ToolResult:
    """
    Enhanced search tool for Arabic RAG processing
    """
    processor = ArabicRAGProcessor(search_client)
    query = args["query"]
    
    # Perform Arabic-optimized search
    results = await processor.search_arabic_content(query)
    
    if not results:
        # Provide helpful suggestions in Arabic
        suggestion_text = """
        عذراً، لم أجد هذا المنتج. جرب البحث عن:
        🍕 بيتزا (فراخ، سي فود، كابوريا)
        🍔 برجر (بيف، دجاج، تشيزي)
        🥘 كالزونى (فراخ، باربكيو، كرسبي)
        أو قل 'اعرض كل المنتجات'
        """
        return ToolResult(suggestion_text, ToolResultDirection.TO_SERVER)
    
    # Format results for voice response
    response_text = "\n".join([r["formatted_display"] for r in results])
    return ToolResult(response_text, ToolResultDirection.TO_SERVER)
```

### Advanced Search Features

```python
# Enhanced search with smart suggestions
class SmartSearchSuggestions:
    
    CATEGORY_KEYWORDS = {
        "pizza": ["بيتزا", "pizza"],
        "burger": ["برجر", "burger"],
        "calzone": ["كالزونى", "calzone"],
        "chicken": ["فراخ", "دجاج", "chicken"],
        "crispy": ["كرسبي", "crispy"],
        "barbecue": ["باربكيو", "barbecue"]
    }
    
    async def get_smart_suggestions(self, query: str, search_client: SearchClient) -> List[str]:
        """
        Generate smart suggestions based on query analysis
        """
        suggestions = []
        
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(keyword in query.lower() for keyword in keywords):
                # Find related items in this category
                category_results = await search_client.search(
                    search_text=" OR ".join(keywords),
                    top=3,
                    select="Name"
                )
                
                async for result in category_results:
                    suggestions.append(result["Name"])
        
        return suggestions[:5]  # Limit to top 5 suggestions
```

## 🌐 WebSocket Real-time Communication

### Frontend WebSocket Client

```typescript
// app/frontend/src/hooks/useRealtime.tsx
import { useEffect, useRef, useState } from 'react';

export interface RealtimeConfig {
  serverUrl: string;
  audioFormat: 'pcm16' | 'g711_ulaw' | 'g711_alaw';
  sampleRate: number;
}

export const useRealtime = (config: RealtimeConfig) => {
  const wsRef = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [conversationState, setConversationState] = useState<'idle' | 'listening' | 'speaking'>('idle');

  const connect = useCallback(async () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(config.serverUrl);
    
    ws.onopen = () => {
      console.log('WebSocket connected to Realtime API');
      setIsConnected(true);
      
      // Send initial configuration
      ws.send(JSON.stringify({
        type: 'session.update',
        session: {
          modalities: ['text', 'audio'],
          instructions: 'أنت مساعد ذكي في مطعم عربي. ساعد العملاء في طلب الطعام واستخدم أدوات البحث للعثور على المنتجات.',
          voice: 'alloy',
          input_audio_format: config.audioFormat,
          output_audio_format: config.audioFormat,
          input_audio_transcription: { model: 'whisper-1' }
        }
      }));
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      handleRealtimeMessage(message);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
    };

    wsRef.current = ws;
  }, [config]);

  const handleRealtimeMessage = (message: any) => {
    switch (message.type) {
      case 'response.audio.delta':
        // Handle incoming audio data
        playAudioDelta(message.delta);
        break;
        
      case 'response.text.delta':
        // Handle text response
        console.log('Text response:', message.delta);
        break;
        
      case 'conversation.item.created':
        // Handle conversation updates
        updateConversationState(message);
        break;
    }
  };

  return {
    connect,
    isConnected,
    conversationState,
    sendAudio: (audioData: ArrayBuffer) => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          type: 'input_audio_buffer.append',
          audio: arrayBufferToBase64(audioData)
        }));
      }
    }
  };
};
```

### Backend WebSocket Handler

```python
# app/backend/rtmt.py - Enhanced for Arabic RAG
import asyncio
import json
import logging
from typing import Dict, Any
from aiohttp import web, WSMsgType
from azure.cognitiveservices.speech import SpeechConfig, AudioConfig

class EnhancedRTMiddleTier:
    def __init__(self, azure_openai_endpoint: str, azure_openai_key: str):
        self.azure_openai_endpoint = azure_openai_endpoint
        self.azure_openai_key = azure_openai_key
        self.active_connections: Dict[str, web.WebSocketResponse] = {}
        
    async def handle_websocket(self, request: web.Request) -> web.WebSocketResponse:
        """
        Enhanced WebSocket handler with Arabic RAG support
        """
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        connection_id = id(ws)
        self.active_connections[connection_id] = ws
        
        logging.info(f"New WebSocket connection: {connection_id}")
        
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    await self.handle_message(connection_id, json.loads(msg.data))
                elif msg.type == WSMsgType.ERROR:
                    logging.error(f"WebSocket error: {ws.exception()}")
                    
        except Exception as e:
            logging.error(f"WebSocket error: {e}")
        finally:
            del self.active_connections[connection_id]
            logging.info(f"WebSocket connection closed: {connection_id}")
            
        return ws
    
    async def handle_message(self, connection_id: str, message: Dict[str, Any]) -> None:
        """
        Process incoming WebSocket messages with RAG integration
        """
        message_type = message.get('type')
        
        if message_type == 'session.update':
            await self.setup_arabic_session(connection_id, message)
        elif message_type == 'input_audio_buffer.append':
            await self.process_audio_input(connection_id, message)
        elif message_type == 'conversation.item.create':
            await self.handle_conversation_item(connection_id, message)
    
    async def setup_arabic_session(self, connection_id: str, message: Dict[str, Any]) -> None:
        """
        Configure session for Arabic language support
        """
        session_config = {
            'instructions': message['session'].get('instructions', 
                'أنت مساعد ذكي في مطعم عربي. استخدم أدوات البحث للمساعدة في العثور على المنتجات.'),
            'modalities': ['text', 'audio'],
            'voice': 'alloy',
            'tools': self.get_arabic_rag_tools(),
            'temperature': 0.7,
            'max_response_output_tokens': 4096
        }
        
        # Send session configuration to Azure OpenAI
        await self.send_to_azure_openai(connection_id, {
            'type': 'session.update',
            'session': session_config
        })
    
    def get_arabic_rag_tools(self) -> List[Dict[str, Any]]:
        """
        Define RAG tools for Arabic search
        """
        return [
            {
                "type": "function",
                "name": "search",
                "description": "البحث في قاعدة المعرفة العربية للمطعم. ابحث عن المنتجات والأسعار والمكونات.",
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
            },
            {
                "type": "function", 
                "name": "show_all_items",
                "description": "عرض جميع المنتجات المتاحة في المطعم",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            }
        ]
```

## 📊 Performance Optimization

### Audio Optimization

```typescript
// Audio buffer management for low latency
class OptimizedAudioProcessor {
  private audioContext: AudioContext;
  private workletNode: AudioWorkletNode;
  
  constructor() {
    this.audioContext = new AudioContext({ sampleRate: 24000 });
    this.initializeWorklet();
  }
  
  async initializeWorklet(): Promise<void> {
    await this.audioContext.audioWorklet.addModule('/audio-processor-worklet.js');
    this.workletNode = new AudioWorkletNode(this.audioContext, 'audio-processor');
    
    // Configure for real-time processing
    this.workletNode.port.onmessage = (event) => {
      const { audioData, timestamp } = event.data;
      this.processAudioData(audioData, timestamp);
    };
  }
  
  private processAudioData(audioData: Float32Array, timestamp: number): void {
    // Convert to 16-bit PCM for Azure OpenAI
    const pcm16Data = this.convertToPCM16(audioData);
    
    // Send to WebSocket with minimal delay
    this.sendAudioToServer(pcm16Data, timestamp);
  }
  
  private convertToPCM16(float32Data: Float32Array): Int16Array {
    const pcm16 = new Int16Array(float32Data.length);
    for (let i = 0; i < float32Data.length; i++) {
      const sample = Math.max(-1, Math.min(1, float32Data[i]));
      pcm16[i] = sample < 0 ? sample * 0x8000 : sample * 0x7FFF;
    }
    return pcm16;
  }
}
```

### Search Performance

```python
# Optimized search with caching
from functools import lru_cache
import asyncio

class PerformantArabicSearch:
    def __init__(self, search_client: SearchClient):
        self.search_client = search_client
        self._search_cache = {}
    
    @lru_cache(maxsize=100)
    async def cached_search(self, query: str) -> List[Dict[str, Any]]:
        """
        Cached search for frequently requested items
        """
        cache_key = f"search:{query.lower()}"
        
        if cache_key in self._search_cache:
            return self._search_cache[cache_key]
        
        # Perform search with optimized parameters
        results = await self.search_client.search(
            search_text=query,
            query_type="simple",
            search_mode="any",
            top=5,
            select="ID,Name,ingredients,Price",
            minimum_coverage=80,  # Ensure good result quality
            timeout=200  # 200ms timeout for fast response
        )
        
        processed_results = []
        async for result in results:
            processed_results.append(result)
        
        # Cache results for 5 minutes
        self._search_cache[cache_key] = processed_results
        asyncio.create_task(self._expire_cache_entry(cache_key, 300))
        
        return processed_results
    
    async def _expire_cache_entry(self, cache_key: str, delay: int) -> None:
        await asyncio.sleep(delay)
        self._search_cache.pop(cache_key, None)
```

---

*This technical guide provides the implementation details for building the 3-stage audio sequence with Arabic RAG integration.* 🔧
