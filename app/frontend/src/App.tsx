import { useState } from "react";
import { Mic, Square } from "lucide-react";

import { Button } from "@/components/ui/button";
import { GroundingFiles } from "@/components/ui/grounding-files";

import useRealTime from "@/hooks/useRealtime";
import useAudioRecorder from "@/hooks/useAudioRecorder";
import useAudioPlayer from "@/hooks/useAudioPlayer";

import { GroundingFile } from "./types";
import GroundingFileView from "./components/ui/grounding-file-view";

// Use "wss://YOUR_INSTANCE_NAME.openai.azure.com" to bypass the middle tier and go directly to the LLM endpoint
const AOAI_ENDPOINT_OVERRIDE = null;
const AOAI_KEY = "none"; // Use a real key if bypassing the middle tier

function App() {
    const [isRecording, setIsRecording] = useState(false);
    // const [transcript, setTranscript] = useState<string[]>([]);
    const [groundingFiles, setGroundingFiles] = useState<GroundingFile[]>([]);
    const [selectedFile, setSelectedFile] = useState<GroundingFile | null>(null);

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
                setGroundingFiles([
                    {
                        name: "fake-search-regions.md",
                        content: "This is a random piece of text that takes more than two lines in the popup for testing purposes.",
                        url: ""
                    },
                    { name: "fake-search-skus.md", content: "", url: "" },
                    { name: "fake-search-documentation-large.md", content: "", url: "" }
                ]);
            }, 1000);
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
            </main>

            <footer className="py-4 text-center text-gray-400">
                <p>Powered by AI Search + Azure OpenAI</p>
            </footer>

            <GroundingFileView groundingFile={selectedFile} onClosed={() => setSelectedFile(null)} />
        </div>
    );
}

export default App;
