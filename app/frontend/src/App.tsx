import { useState } from "react";

import { Button } from "@/components/ui/button";

import useRealTime from "@/hooks/useRealtime";
import useAudioRecorder from "@/hooks/useAudioRecorder";
import useAudioPlayer from "@/hooks/useAudioPlayer";

import "./App.css";

// Use "wss://YOUR_INSTANCE_NAME.openai.azure.com" to bypass the middle tier and go directly to the LLM endpoint
const AOAI_ENDPOINT_OVERRIDE = null;
const AOAI_KEY = "none"; // Use a real key if bypassing the middle tier

function App() {
    const [recording, setRecording] = useState(false);

    const { startSession, addUserAudio } = useRealTime({
        aoaiEndpointOverride: AOAI_ENDPOINT_OVERRIDE,
        aoaiApiKey: AOAI_KEY,
        onWebSocketOpen: () => console.log("WebSocket connection opened"),
        onWebSocketClose: () => console.log("WebSocket connection closed"),
        onWebSocketError: event => console.error("WebSocket error:", event),
        onReceivedStartSession: () => console.log("start_session"),
        onReceivedAddMessage: () => console.log("add_message"),
        onReceivedAddContent: message => {
            if (message.type === "text") {
                console.log(message.data);
            } else if (message.type === "audio") {
                playAudio(message.data);
            }
        },
        onReceivedInputTranscribed: () => console.log("input_transcribed"),
        onReceivedGenerationCanceled: () => console.log("generation_canceled"),
        onReceivedGenerationFinished: () => console.log("generation_finished"),
        onReceivedVadSpeechStarted: () => console.log("vad_speech_started"),
        onReceivedVadSpeechStopped: () => console.log("vad_speech_stopped"),
        onReceivedError: () => console.error("error")
    });

    const { reset: resetAudioPlayer, play: playAudio, stop: stopAudioPlayer } = useAudioPlayer();
    const { start: startAudioRecording, stop: stopAudioRecording } = useAudioRecorder({ onAudioRecorded: addUserAudio });

    const onTalk = async () => {
        if (!recording) {
            startSession();

            startAudioRecording();
            resetAudioPlayer();

            setRecording(true);
        } else {
            stopAudioRecording();
            stopAudioPlayer();

            setRecording(false);
        }
    };

    return (
        <div className="min-h-screen p-8 place-content-center">
            <div className="flex flex-col text-center space-y-8">
                <h1>Talk to your data</h1>
                <div>
                    <div className="flex justify-center space-x-2 mb-4">
                        <Button variant="outline" className="talkButton" onClick={onTalk}>
                            {recording ? "Stop" : "Start"}
                        </Button>
                    </div>
                    <p className="note mb-8">{recording ? "Listening..." : "Press to start talking"}</p>
                </div>
            </div>
        </div>
    );
}

export default App;
