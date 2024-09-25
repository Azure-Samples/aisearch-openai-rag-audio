import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { File, Mic, StopCircle, ChevronDown, ChevronUp } from "lucide-react";

import { Button } from "@/components/ui/button";

import useRealTime from "@/hooks/useRealtime";
import useAudioRecorder from "@/hooks/useAudioRecorder";
import useAudioPlayer from "@/hooks/useAudioPlayer";

import "./App.css";

// Use "wss://YOUR_INSTANCE_NAME.openai.azure.com" to bypass the middle tier and go directly to the LLM endpoint
const AOAI_ENDPOINT_OVERRIDE = null;
const AOAI_KEY = "none"; // Use a real key if bypassing the middle tier

function App() {
    const [isRecording, setIsRecording] = useState(false);
    const [showTranscript, setShowTranscript] = useState(false);

    const [log, setLog] = useState<string[]>([]);
    const [ragFiles, setRagFiles] = useState<string[]>([]);

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
            setLog(log => [...log, message.delta]);
        },
        onReceivedResponseAudioTranscriptDone: () => {
            setLog(log => [...log, "\n"]);
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
        // onReceivedInputTranscribed: () => {
        //     console.log("input_transcribed");
        // },
        // onReceivedGenerationCanceled: () => console.log("generation_canceled"),
        // onReceivedGenerationFinished: () => {
        //     console.log("generation_finished");
        //     log.push("\n");
        // },
        // onReceivedVadSpeechStarted: () => console.log("vad_speech_started"),
        // onReceivedVadSpeechStopped: () => console.log("vad_speech_stopped"),
        onReceivedError: message => console.error("error", message)
    });

    const { reset: resetAudioPlayer, play: playAudio, stop: stopAudioPlayer } = useAudioPlayer();
    const { start: startAudioRecording, stop: stopAudioRecording } = useAudioRecorder({ onAudioRecorded: addUserAudio });

    const onTalk = async () => {
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
        }
    };

    return (
        <div className="flex flex-col min-h-screen bg-gray-100 text-gray-900">
            <main className="flex-grow flex flex-col items-center justify-center p-6">
                <h1 className="text-3xl md:text-4xl lg:text-7xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-600 to-pink-600 mb-8">
                    Talk to your data
                </h1>
                <div className="flex justify-center mb-4">
                    <Button
                        onClick={onTalk}
                        className={`w-full md:w-auto ${isRecording ? "bg-red-500 hover:bg-red-600 " : "bg-purple-500 hover:bg-purple-600"}`}
                    >
                        {isRecording ? (
                            <>
                                <StopCircle className="w-5 h-5 mr-2" />
                                Stop
                            </>
                        ) : (
                            <>
                                <Mic className="w-5 h-5 mr-2" />
                                Start talking
                            </>
                        )}
                    </Button>
                </div>
                <div className="w-full max-w-md bg-white rounded-lg shadow-lg p-6 border border-gray-200">
                    {ragFiles.length > 0 && (
                        <div className="mb-6">
                            <h3 className="text-sm font-medium mb-2">Files used to ground answers:</h3>
                            <div className="flex flex-wrap gap-2">
                                {ragFiles.map((file, index) => (
                                    <Button key={index} variant="outline" size="sm" className="rounded-full">
                                        <File className="w-4 h-4 mr-2" />
                                        {file}
                                    </Button>
                                ))}
                            </div>
                        </div>
                    )}

                    <div className="border-gray-200">
                        <Button
                            disabled={log.length === 0}
                            onClick={() => setShowTranscript(!showTranscript)}
                            variant="outline"
                            className="w-full text-gray-700 border-gray-300  hover:bg-gray-100"
                        >
                            {showTranscript ? (
                                <>
                                    <ChevronUp className="w-5 h-5 mr-2" />
                                    Hide generation transcript
                                </>
                            ) : (
                                <>
                                    <ChevronDown className="w-5 h-5 mr-2" />
                                    Show generation transcript
                                </>
                            )}
                        </Button>

                        <AnimatePresence>
                            {showTranscript && (
                                <motion.div
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: "auto" }}
                                    exit={{ opacity: 0, height: 0 }}
                                    transition={{ duration: 0.3 }}
                                    className="mt-4 bg-gray-100 rounded-lg p-4 overflow-y-auto max-h-60"
                                >
                                    {log.map(item => {
                                        if (item === "\n") {
                                            return <br />;
                                        }

                                        return item;
                                    })}
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                </div>
            </main>

            <footer className="py-4 text-center text-gray-400">
                <p>Powered by AI Search + Azure OpenAI</p>
            </footer>
        </div>
    );
}

export default App;
