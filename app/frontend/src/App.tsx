import { useState } from "react";
import useWebSocket from "react-use-websocket";

import { Button } from "@/components/ui/button";
import { Player } from "@/components/audio/player";
import { Recorder } from "@/components/audio/recorder";

import "./App.css";

// Use "wss://YOUR_INSTANCE_NAME.openai.azure.com" to bypass the middle tier and go directly to the LLM endpoint
const AOAI_ENDPOINT_OVERRIDE = null;
const AOAI_KEY = "none"; // Use a real key if bypassing the middle tier

const BUFFER_SIZE = 4800;
const SAMPLE_RATE = 24000;
let buffer: Uint8Array = new Uint8Array();
let audioRecorder: Recorder;
let audioPlayer: Player;

function App() {
    const [recording, setRecording] = useState(false);

    const onMessageReceived = (event: MessageEvent<any>) => {
        console.log("Websocket onMessage:", event);

        const message = JSON.parse(event.data);

        switch (message.event) {
            case "start_session":
                console.log("start_session");
                break;
            case "add_message":
                console.log("add_message");
                break;
            case "add_content":
                console.log("add_content");

                if (message.type === "text") {
                    console.log(message.data);
                } else if (message.type === "audio") {
                    const binary = atob(message.data);
                    const bytes = Uint8Array.from(binary, c => c.charCodeAt(0));
                    const pcmData = new Int16Array(bytes.buffer);
                    audioPlayer.play(pcmData);
                }

                break;
            case "input_transcribed":
                console.log("input_transcribed");
                break;
            case "generation_canceled":
                console.log("generation_canceled");
                break;
            case "generation_finished":
                console.log("generation_finished");
                break;
            case "vad_speech_started":
                console.log("vad_speech_started");
                break;
            case "vad_speech_stopped":
                console.log("vad_speech_stopped");
                break;
            case "error":
                console.log("error");
                break;
        }
    };

    const { sendJsonMessage } = useWebSocket(`${AOAI_ENDPOINT_OVERRIDE ?? ""}/realtime?api-key=${AOAI_KEY}&api-version=alpha`, {
        onOpen: () => console.log("Websocket connection opened"),
        onClose: () => console.log("Websocket connection closed"),
        onError: event => console.error("WebSocket error:", event),
        onMessage: onMessageReceived
    });

    function combineArray(newData: Uint8Array) {
        const newBuffer = new Uint8Array(buffer.length + newData.length);
        newBuffer.set(buffer);
        newBuffer.set(newData, buffer.length);
        buffer = newBuffer;
    }

    function processAudioRecordingBuffer(data: Iterable<number>) {
        const uint8Array = new Uint8Array(data);
        combineArray(uint8Array);

        if (buffer.length >= BUFFER_SIZE) {
            const toSend = new Uint8Array(buffer.slice(0, BUFFER_SIZE));
            buffer = new Uint8Array(buffer.slice(BUFFER_SIZE));

            const regularArray = String.fromCharCode(...toSend);
            const base64 = btoa(regularArray);

            sendJsonMessage({
                event: "add_user_audio",
                data: base64
            });
        }
    }

    const onTalk = async () => {
        if (!recording) {
            sendJsonMessage({
                event: "update_session_config",
                turn_detection: "server_vad"
            });

            sendJsonMessage({
                event: "update_conversation_config"
            });

            audioRecorder = new Recorder(processAudioRecordingBuffer);

            audioPlayer = new Player();
            audioPlayer.init(SAMPLE_RATE);

            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            audioRecorder.start(stream);

            setRecording(true);
        } else {
            if (audioRecorder) {
                audioRecorder.stop();
            }

            if (audioPlayer) {
                audioPlayer.stop();
            }

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
