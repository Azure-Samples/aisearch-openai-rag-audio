import { useState } from "react";
import { Mic, History, MicOff } from "lucide-react";
import { motion } from "framer-motion";

import { Button } from "@/components/ui/button";
import { GroundingFiles } from "@/components/ui/grounding-files";
import GroundingFileView from "@/components/ui/grounding-file-view";
import HistoryPanel from "@/components/ui/history-panel";

import useRealTime from "@/hooks/useRealtime";
import useAudioRecorder from "@/hooks/useAudioRecorder";
import useAudioPlayer from "@/hooks/useAudioPlayer";

import { GroundingFile, HistoryItem, ToolResult } from "./types";

// Use "wss://YOUR_INSTANCE_NAME.openai.azure.com" to bypass the middle tier and go directly to the LLM endpoint
const AOAI_ENDPOINT_OVERRIDE = null;
const AOAI_KEY = "none"; // Use a real key if bypassing the middle tier

const HISTORY_ENABLED = false;

function App() {
    const [isRecording, setIsRecording] = useState(false);
    const [groundingFiles, setGroundingFiles] = useState<GroundingFile[]>([]);
    const [selectedFile, setSelectedFile] = useState<GroundingFile | null>(null);

    const [showHistory, setShowHistory] = useState(false);
    const [history, setHistory] = useState<HistoryItem[]>([]);

    const { startSession, addUserAudio, inputAudioBufferClear } = useRealTime({
        aoaiEndpointOverride: AOAI_ENDPOINT_OVERRIDE,
        aoaiApiKey: AOAI_KEY,
        onWebSocketOpen: () => console.log("WebSocket connection opened"),
        onWebSocketClose: () => console.log("WebSocket connection closed"),
        onWebSocketError: event => console.error("WebSocket error:", event),
        onReceivedError: message => console.error("error", message),
        onReceivedResponseAudioDelta: message => {
            isRecording && playAudio(message.delta);
        },
        onReceivedInputAudioBufferSpeechStarted: () => {
            stopAudioPlayer();
        },
        onReceivedResponseDone: message => {
            if (!HISTORY_ENABLED || message.response.output?.length === 0 || !message.response.output.some(x => !!x.content?.length)) {
                return;
            }

            setHistory(prev => [
                ...prev,
                ...message.response.output.flatMap(o => o.content?.flatMap(c => ({ id: o.id, transcript: c.transcript, groundingFiles: [] })) ?? [])
            ]);
        },
        onReceivedExtensionMiddleTierToolResponse: message => {
            const result: ToolResult = JSON.parse(message.tool_result);

            const files: GroundingFile[] = result.sources.map(x => {
                const match = x.chunk_id.match(/_pages_(\d+)$/);
                const name = match ? `${x.title}#page=${match[1]}` : x.title;
                return { id: x.chunk_id, name: name, content: x.chunk };
            });

            setGroundingFiles(prev => [...prev, ...files]);
        }
    });

    const { reset: resetAudioPlayer, play: playAudio, stop: stopAudioPlayer } = useAudioPlayer();
    const { start: startAudioRecording, stop: stopAudioRecording } = useAudioRecorder({ onAudioRecorded: addUserAudio });

    const onToggleListening = async () => {
        if (!isRecording) {
            startSession();
            await startAudioRecording();
            resetAudioPlayer();

            setIsRecording(true);
        } else {
            await stopAudioRecording();
            stopAudioPlayer();
            inputAudioBufferClear();

            setIsRecording(false);
        }
    };

    return (
        <div className="flex min-h-screen flex-col bg-gray-100 text-gray-900">
            <main className="flex flex-grow flex-col items-center justify-center">
                <h1 className="mb-8 bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-4xl font-bold text-transparent md:text-7xl">
                    Talk to your data
                </h1>
                <div className="mb-4 flex flex-col items-center justify-center">
                    <Button
                        onClick={onToggleListening}
                        className={`h-12 w-60 ${isRecording ? "bg-red-500 hover:bg-red-600" : "bg-purple-500 hover:bg-purple-600"}`}
                        aria-label={isRecording ? "Stop recording" : "Start recording"}
                    >
                        {isRecording ? (
                            <>
                                <MicOff className="mr-2 h-4 w-4" />
                                Stop conversation
                            </>
                        ) : (
                            <>
                                <Mic className="mr-2 h-6 w-6" />
                            </>
                        )}
                    </Button>
                    {isRecording ? (
                        <div className="flex items-center">
                            <motion.div
                                animate={{ opacity: [1, 0.5, 1] }}
                                transition={{ repeat: Infinity, duration: 1 }}
                                className="mr-2 mt-2 h-3 w-3 rounded-full bg-red-500"
                            />
                            <p className="text mb-4 mt-6 text-gray-500">Conversation in progress...</p>
                        </div>
                    ) : (
                        <p className="text mb-4 mt-6 text-gray-500">Ask anything about your knowledge base</p>
                    )}
                </div>
                <GroundingFiles files={groundingFiles} onSelected={setSelectedFile} />
                {HISTORY_ENABLED && history.length > 0 && (
                    <Button variant="outline" size="sm" onClick={() => setShowHistory(!showHistory)} className="rounded-full">
                        <History className="mr-2 h-4 w-4" />
                        Show history
                    </Button>
                )}
            </main>

            <footer className="py-4 text-center text-gray-400">
                <p>Powered by AI Search + Azure OpenAI</p>
            </footer>

            <GroundingFileView groundingFile={selectedFile} onClosed={() => setSelectedFile(null)} />
            <HistoryPanel history={history} show={showHistory} onClosed={() => setShowHistory(false)} onSelectedGroundingFile={file => setSelectedFile(file)} />
        </div>
    );
}

export default App;
