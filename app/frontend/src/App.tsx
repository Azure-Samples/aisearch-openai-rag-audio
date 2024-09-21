import { useCallback, useRef, useState } from "react";
import useWebSocket, { ReadyState } from "react-use-websocket";
import { Settings as SettingsIcon } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Player } from "@/components/audio/player";
import { Recorder } from "@/components/audio/recorder";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

import { Settings } from "./types";

import "./App.css";

const AOAI_ENDPOINT = "YOUR_INSTANCE_NAME.openai.azure.com";
const AOAI_KEY = "YOUR_API_KEY";

const BUFFER_SIZE = 4800;
const SAMPLE_RATE = 24000;
let buffer: Uint8Array = new Uint8Array();
let audioRecorder: Recorder;
let audioPlayer: Player;

function App() {
    const [isSettingsOpen, setIsSettingsOpen] = useState(false);
    const [settings, setSettings] = useState<Settings>({
        temperature: 0.8,
        systemPrompt: "",
        voice: "alloy"
    });
    const settingsRef = useRef<HTMLDivElement>(null);

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

    const { sendJsonMessage, lastJsonMessage, readyState } = useWebSocket(`wss://${AOAI_ENDPOINT}/realtime?api-key=${AOAI_KEY}&api-version=alpha`, {
        onOpen: () => console.log("Websocket connection opened"),
        onClose: () => console.log("Websocket connection closed"),
        onError: event => console.error("WebSocket error:", event),
        onMessage: onMessageReceived
    });

    const connectionStatus = {
        [ReadyState.CONNECTING]: "Connecting",
        [ReadyState.OPEN]: "Open",
        [ReadyState.CLOSING]: "Closing",
        [ReadyState.CLOSED]: "Closed",
        [ReadyState.UNINSTANTIATED]: "Uninstantiated"
    }[readyState];

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
                event: "update_conversation_config",
                system_message: settings.systemPrompt,
                temperature: settings.temperature,
                voice: settings.voice
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

    const toggleSettings = useCallback(() => {
        setIsSettingsOpen(prev => !prev);
    }, []);

    const updateSetting = useCallback((key: string, value: any) => {
        setSettings(prev => ({ ...prev, [key]: value }));
    }, []);

    return (
        <div className="min-h-screen p-8 place-content-center">
            <div className="flex flex-col text-center space-y-8">
                <h1>Talk to your data</h1>
                <div>
                    <div className="flex justify-center space-x-2 mb-4">
                        <Button variant="outline" className="talkButton" onClick={onTalk}>
                            {recording ? "Stop" : "Start"}
                        </Button>
                        <Button onClick={toggleSettings} variant="outline" size="icon" aria-label={isSettingsOpen ? "Close settings" : "Open settings"}>
                            <SettingsIcon className="h-4 w-4" />
                        </Button>
                    </div>

                    <p className="note mb-8">{recording ? "Listening..." : "Press to start talking"}</p>
                    <p className="note">Websocket status: {connectionStatus}</p>
                    <p className="note">Websocket last message: {lastJsonMessage ? JSON.stringify(lastJsonMessage) : ""}</p>
                </div>
            </div>

            <div
                className={`fixed top-0 right-0 h-full w-80 bg-background shadow-lg transform transition-transform duration-300 ease-in-out ${
                    isSettingsOpen ? "translate-x-0" : "translate-x-full"
                }`}
                ref={settingsRef}
            >
                <div className="p-4 space-y-6">
                    <h2 className="text-2xl font-bold mb-4">Settings</h2>

                    <div className="space-y-2">
                        <Label htmlFor="temperature">Temperature: {settings.temperature.toFixed(1)}</Label>
                        <Slider
                            id="temperature"
                            min={0}
                            max={1}
                            step={0.1}
                            value={[settings.temperature]}
                            onValueChange={value => updateSetting("temperature", value[0])}
                        />
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="systemPrompt">System prompt</Label>
                        <Textarea
                            id="systemPrompt"
                            value={settings.systemPrompt}
                            onChange={e => updateSetting("systemPrompt", e.target.value)}
                            placeholder="Enter system prompt here..."
                            className="h-32"
                        />
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="voice">Voice</Label>
                        <Select value={settings.voice} onValueChange={value => updateSetting("voice", value)}>
                            <SelectTrigger id="voice">
                                <SelectValue placeholder="Select a voice" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="alloy">alloy</SelectItem>
                                <SelectItem value="echo">echo</SelectItem>
                                <SelectItem value="shimmer">shimmer</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default App;
