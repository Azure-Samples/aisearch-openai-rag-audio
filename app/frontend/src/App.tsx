import { useState } from "react";
import { Mic, Square } from "lucide-react";

import { Button } from "@/components/ui/button";
import { GroundingFiles } from "@/components/ui/grounding-files";

import useRealTime from "@/hooks/useRealtime";
import useAudioRecorder from "@/hooks/useAudioRecorder";
import useAudioPlayer from "@/hooks/useAudioPlayer";

// Use "wss://YOUR_INSTANCE_NAME.openai.azure.com" to bypass the middle tier and go directly to the LLM endpoint
const AOAI_ENDPOINT_OVERRIDE = null;
const AOAI_KEY = "none"; // Use a real key if bypassing the middle tier

function App() {
    const [isRecording, setIsRecording] = useState(false);
    // const [transcript, setTranscript] = useState<string[]>([]);
    const [groundingFiles, setGroundingFiles] = useState<string[]>([]);

    const { startSession, addUserAudio, inputAudioBufferClear } = useRealTime({
        aoaiEndpointOverride: AOAI_ENDPOINT_OVERRIDE,
        aoaiApiKey: AOAI_KEY,
        onWebSocketOpen: () => console.log("WebSocket connection opened"),
        onWebSocketClose: () => console.log("WebSocket connection closed"),
        onWebSocketError: event => console.error("WebSocket error:", event),
        onWebSocketMessage: event => console.log("WebSocket message:", event),

        onReceivedResponseAudioDelta: message => {
            playAudio(message.delta);
        },
        onReceivedResponseAudioTranscriptDelta: message => {
            console.log(message.delta);
            // setTranscript(log => [...log, message.delta]);
        },
        onReceivedResponseAudioTranscriptDone: () => {
            // setTranscript(log => [...log, "\n"]);
        },

        // onReceivedAddContent: message => {
        //     if (message.type === "text") {
        //         console.log(message.data);
        //         setLog(log => [...log, message.data]);
        //     } else if (message.type === "audio") {
        //         playAudio(message.data);
        //     } else if (!message.type && message.message?.content) {
        //         const fileNames = message.message.content.flatMap(item => {
        //             const match = /\*\*\*grounding:(\S+)/.exec(item.text);
        //             return match ? [match[1]] : [];
        //         });

        //         setRagFiles(prev => [...prev, ...fileNames]);
        //     }
        // },
        onReceivedError: message => console.error("error", message)
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
                // setTranscript(["Hi", " !", "this", "\n", "is", "a", "test", "rrrandomg randomg randomg randomg rhiajisd"]);
                setGroundingFiles(["fake-search-regions.md", "fake-search-doc.md"]);
            }, 1000);
        }
    };

    return (
        <div className="flex flex-col min-h-screen bg-gray-100 text-gray-900">
            <main className="flex-grow flex flex-col items-center justify-center">
                <h1 className="text-3xl md:text-4xl lg:text-7xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-600 to-pink-600 mb-8">
                    Talk to your data
                </h1>
                <div className="flex justify-center mb-4">
                    <Button
                        onClick={onToggleListening}
                        className={`w-full md:w-auto lg:w-60 lg:h-12 ${isRecording ? "bg-red-500 hover:bg-red-600 " : "bg-purple-500 hover:bg-purple-600"}`}
                        aria-label={isRecording ? "Stop recording" : "Start recording"}
                    >
                        {isRecording ? (
                            <>
                                <Square className="w-6 h-6 mr-2" />
                                Stop
                            </>
                        ) : (
                            <>
                                <Mic className="w-6 h-6 mr-2" />
                            </>
                        )}
                    </Button>
                </div>

                <div className="flex flex-wrap justify-center gap-4">
                    <GroundingFiles files={groundingFiles} />
                </div>
            </main>

            <footer className="py-4 text-center text-gray-400">
                <p>Powered by AI Search + Azure OpenAI</p>
            </footer>
        </div>
    );
}

export default App;
