import { useState } from "react";
import { Mic, MicOff } from "lucide-react";
import { useTranslation } from "react-i18next";

import { Button } from "@/components/ui/button";
import GroundingFileView from "@/components/ui/grounding-file-view";
import StatusMessage from "@/components/ui/status-message";
import HistoryPanel from "@/components/ui/history-panel";

import useRealTime from "@/hooks/useRealtime";
import useAudioRecorder from "@/hooks/useAudioRecorder";
import useAudioPlayer from "@/hooks/useAudioPlayer";

import { GroundingFile, HistoryItem, ToolResult } from "./types";

import logo from "./assets/logo.svg";

function App() {
    const [isRecording, setIsRecording] = useState(false);
    const [selectedFile, setSelectedFile] = useState<GroundingFile | null>(null);
    const [groundingFiles, setGroundingFiles] = useState<GroundingFile[]>([]);
    const [showTranscript, setShowTranscript] = useState(false);
    const [history, setHistory] = useState<HistoryItem[]>([]);

    const { startSession, addUserAudio, inputAudioBufferClear } = useRealTime({
        enableInputAudioTranscription: true, // Enable input audio transcription from the user to show in the history
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
        onReceivedExtensionMiddleTierToolResponse: message => {
            const result: ToolResult = JSON.parse(message.tool_result);
            const files: GroundingFile[] = result.sources.map(x => {
                return { id: x.chunk_id, name: x.title, content: x.chunk };
            });

            setGroundingFiles(files); // Store the grounding files for the assistant
        },
        onReceivedInputAudioTranscriptionCompleted: message => {
            // Update history with input audio transcription when completed
            const newHistoryItem: HistoryItem = {
                id: message.event_id,
                transcript: message.transcript,
                groundingFiles: [],
                sender: "user",
                timestamp: new Date() // Add timestamp
            };
            setHistory(prev => [...prev, newHistoryItem]);
        },
        onReceivedResponseDone: message => {
            const transcript = message.response.output.map(output => output.content?.map(content => content.transcript).join(" ")).join(" ");
            if (!transcript) {
                return;
            }

            // Update history with response done
            const newHistoryItem: HistoryItem = {
                id: message.event_id,
                transcript: transcript,
                groundingFiles: groundingFiles,
                sender: "assistant",
                timestamp: new Date() // Add timestamp
            };
            setHistory(prev => [...prev, newHistoryItem]);
            setGroundingFiles([]); // Clear the assistant grounding files after use
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

    const { t } = useTranslation();

    return (
        <div className="flex min-h-screen flex-col bg-gray-100 text-gray-900">
            <div className="p-4 sm:absolute sm:left-4 sm:top-4">
                <img src={logo} alt="Azure logo" className="h-16 w-16" />
            </div>
            <main className="flex flex-grow flex-col items-center justify-center">
                <h1 className="mb-8 bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-4xl font-bold text-transparent md:text-7xl">
                    {t("app.title")}
                </h1>
                <div className="mb-4 flex flex-col items-center justify-center">
                    <Button
                        onClick={onToggleListening}
                        className={`h-12 w-60 ${isRecording ? "bg-red-600 hover:bg-red-700" : "bg-purple-500 hover:bg-purple-600"}`}
                        aria-label={isRecording ? t("app.stopRecording") : t("app.startRecording")}
                    >
                        {isRecording ? (
                            <>
                                <MicOff className="mr-2 h-4 w-4" />
                                {t("app.stopConversation")}
                            </>
                        ) : (
                            <>
                                <Mic className="mr-2 h-6 w-6" />
                            </>
                        )}
                    </Button>
                    <StatusMessage isRecording={isRecording} />
                </div>
                <div className="mb-4 flex space-x-4">
                    <button
                        onClick={() => setShowTranscript(!showTranscript)}
                        className="text-blue-500 hover:underline focus:outline-none"
                        aria-label={t("app.showTranscript")}
                    >
                        {t("app.showTranscript")}
                    </button>
                </div>
            </main>

            <footer className="py-4 text-center">
                <p>{t("app.footer")}</p>
            </footer>

            <GroundingFileView groundingFile={selectedFile} onClosed={() => setSelectedFile(null)} />

            <HistoryPanel show={showTranscript} history={history} onClosed={() => setShowTranscript(false)} onSelectedGroundingFile={setSelectedFile} />
        </div>
    );
}

export default App;
