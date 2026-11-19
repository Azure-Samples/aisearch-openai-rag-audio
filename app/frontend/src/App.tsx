import { useState } from "react";
import { Mic, MicOff } from "lucide-react";
import { useTranslation } from "react-i18next";

import { Button } from "@/components/ui/button";
import { GroundingFiles } from "@/components/ui/grounding-files";
import GroundingFileView from "@/components/ui/grounding-file-view";
import StatusMessage from "@/components/ui/status-message";

import useRealTime from "@/hooks/useRealtime";
import useAudioRecorder from "@/hooks/useAudioRecorder";
import useAudioPlayer from "@/hooks/useAudioPlayer";
import useAudioSequence from "@/hooks/useAudioSequence";

import { GroundingFile, ToolResult } from "./types";

import logo from "./assets/logo.svg";

function App() {
    const [isRecording, setIsRecording] = useState(false);
    const [isPlayingSequence, setIsPlayingSequence] = useState(false);
    const [groundingFiles, setGroundingFiles] = useState<GroundingFile[]>([]);
    const [selectedFile, setSelectedFile] = useState<GroundingFile | null>(null);

    const { startSession, addUserAudio, inputAudioBufferClear } = useRealTime({
        onWebSocketOpen: () => console.log("WebSocket connection opened"),
        onWebSocketClose: () => console.log("WebSocket connection closed"),
        onWebSocketError: event => console.error("WebSocket error:", event),
        onReceivedError: message => console.error("error", message),
        onReceivedResponseAudioDelta: message => {
            isRecording && playAudio(message.delta);
        },
        onReceivedInputAudioBufferSpeechStarted: () => {
            console.log("Speech started detected");
            stopAudioPlayer();
        },
        onReceivedExtensionMiddleTierToolResponse: message => {
            const result: ToolResult = JSON.parse(message.tool_result);

            const files: GroundingFile[] = result.sources.map(x => {
                return { id: x.chunk_id, name: x.title, content: x.chunk };
            });

            setGroundingFiles(prev => [...prev, ...files]);
        }
    });

    const { reset: resetAudioPlayer, play: playAudio, stop: stopAudioPlayer } = useAudioPlayer();
    const { start: startAudioRecording, stop: stopAudioRecording } = useAudioRecorder({ onAudioRecorded: addUserAudio });

    // Hook للتسلسل الصوتي
    const { playAudioSequence } = useAudioSequence({
        onSequenceComplete: async () => {
            // بعد انتهاء تسلسل الأصوات بالكامل، بدء الريل تايم
            console.log('Audio sequence completed, starting realtime...');
            setIsPlayingSequence(false);
            setIsRecording(true);
            
            // بدء جلسة الريل تايم
            startSession();
            
            // بدء تسجيل الصوت
            await startAudioRecording();
            resetAudioPlayer();
        }
    });

    const onToggleListening = async () => {
        console.log('onToggleListening called. isRecording:', isRecording, 'isPlayingSequence:', isPlayingSequence);
        
        if (!isRecording && !isPlayingSequence) {
            // بدء تسلسل الأصوات
            console.log('Starting audio sequence...');
            setIsPlayingSequence(true);
            playAudioSequence();
        } else if (isRecording) {
            console.log('Stopping recording...');
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
                        className={`h-12 w-60 ${
                            isRecording 
                                ? "bg-red-600 hover:bg-red-700" 
                                : isPlayingSequence 
                                    ? "bg-yellow-500 hover:bg-yellow-600" 
                                    : "bg-purple-500 hover:bg-purple-600"
                        }`}
                        disabled={isPlayingSequence}
                        aria-label={
                            isRecording 
                                ? t("app.stopRecording") 
                                : isPlayingSequence 
                                    ? "جاري التحضير..." 
                                    : t("app.startRecording")
                        }
                    >
                        {isRecording ? (
                            <>
                                <MicOff className="mr-2 h-4 w-4" />
                                {t("app.stopConversation")}
                            </>
                        ) : isPlayingSequence ? (
                            <>
                                <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                                جاري التحضير...
                            </>
                        ) : (
                            <>
                                <Mic className="mr-2 h-6 w-6" />
                                اتصال
                            </>
                        )}
                    </Button>
                    <StatusMessage isRecording={isRecording} isPlayingSequence={isPlayingSequence} />
                </div>
                <GroundingFiles files={groundingFiles} onSelected={setSelectedFile} />
            </main>

            <footer className="py-4 text-center">
                <p>{t("app.footer")}</p>
            </footer>

            <GroundingFileView groundingFile={selectedFile} onClosed={() => setSelectedFile(null)} />
        </div>
    );
}

export default App;
