import { useState } from "react";
import { Mic, Square, History } from "lucide-react";

import { Button } from "@/components/ui/button";
import { GroundingFiles } from "@/components/ui/grounding-files";
import GroundingFileView from "@/components/ui/grounding-file-view";
import HistoryPanel from "@/components/ui/history-panel";

import useRealTime from "@/hooks/useRealtime";
import useAudioRecorder from "@/hooks/useAudioRecorder";
import useAudioPlayer from "@/hooks/useAudioPlayer";

import { GroundingFile, HistoryItem } from "./types";

// Use "wss://YOUR_INSTANCE_NAME.openai.azure.com" to bypass the middle tier and go directly to the LLM endpoint
const AOAI_ENDPOINT_OVERRIDE = null;
const AOAI_KEY = "none"; // Use a real key if bypassing the middle tier

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
        onWebSocketMessage: event => console.log("WebSocket message:", event.data),
        onReceivedError: message => console.error("error", message),
        onReceivedResponseAudioDelta: message => {
            playAudio(message.delta);
        },
        onReceivedResponseDone: message => {
            if (message.response.output?.length === 0 || !message.response.output.some(x => x.content?.length > 0)) {
                return;
            }

            setHistory(prev => [
                ...prev,
                ...message.response.output.flatMap(o => o.content.flatMap(c => ({ id: o.id, answer: c.transcript, groundingFiles: [] })))
            ]);
        }
    });

    const { reset: resetAudioPlayer, play: playAudio, stop: stopAudioPlayer } = useAudioPlayer();
    const { start: startAudioRecording, stop: stopAudioRecording } = useAudioRecorder({ onAudioRecorded: addUserAudio });

    const onToggleListening = async () => {
        if (!isRecording) {
            startSession();

            startAudioRecording();
            resetAudioPlayer();

            setIsRecording(true);
        } else {
            stopAudioRecording();
            stopAudioPlayer();
            inputAudioBufferClear();

            setIsRecording(false);

            setTimeout(() => {
                setGroundingFiles([
                    {
                        name: "fake-search-regions.md",
                        content: "This is a random piece of text that takes more than two lines in the popup for testing purposes.",
                        url: ""
                    },
                    { name: "fake-search-skus.md", content: "", url: "" },
                    { name: "fake-search-documentation-large.md", content: "", url: "" }
                ]);
            }, 500);
        }
    };

    return (
        <div className="flex min-h-screen flex-col bg-gray-100 text-gray-900">
            <main className="flex flex-grow flex-col items-center justify-center">
                <h1 className="mb-8 bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-4xl font-bold text-transparent lg:text-7xl">
                    Talk to your data
                </h1>
                <div className="mb-4 flex justify-center">
                    <Button
                        onClick={onToggleListening}
                        className={`h-12 w-60 ${isRecording ? "bg-red-500 hover:bg-red-600" : "bg-purple-500 hover:bg-purple-600"}`}
                        aria-label={isRecording ? "Stop recording" : "Start recording"}
                    >
                        {isRecording ? (
                            <>
                                <Square className="mr-2 h-6 w-6" />
                                Stop
                            </>
                        ) : (
                            <>
                                <Mic className="mr-2 h-6 w-6" />
                            </>
                        )}
                    </Button>
                </div>
                <GroundingFiles files={groundingFiles} onSelected={setSelectedFile} />
                {history.length > 0 && (
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
