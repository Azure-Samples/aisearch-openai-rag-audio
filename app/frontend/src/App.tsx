import { useState } from "react";
import useWebSocket, { ReadyState } from "react-use-websocket";
import "./App.css";

function App() {
    const [recording, setRecording] = useState(false);

    //Public API that will echo messages sent to it back to the client
    const { sendJsonMessage, lastJsonMessage, readyState } = useWebSocket("wss://echo.websocket.org", {
        onOpen: () => console.log("Websocket connection opened"),
        onClose: () => console.log("Websocket connection closed"),
        onError: event => console.error("WebSocket error:", event),
        onMessage: event => console.log("Websocket onMessage:", event)
    });

    const connectionStatus = {
        [ReadyState.CONNECTING]: "Connecting",
        [ReadyState.OPEN]: "Open",
        [ReadyState.CLOSING]: "Closing",
        [ReadyState.CLOSED]: "Closed",
        [ReadyState.UNINSTANTIATED]: "Uninstantiated"
    }[readyState];

    const onTalk = () => {
        setRecording(!recording);

        if (!recording) {
            sendJsonMessage({ event: "Start talking" });
        } else {
            sendJsonMessage({ event: "Stop talking" });
        }
    };

    return (
        <>
            <h1>Talk to your data</h1>
            <div className="card">
                <button className="button" onClick={onTalk}>
                    {recording ? "Stop" : "Talk"}
                </button>
                <p className="note">{recording ? "Listening..." : "Press to start talking"}</p>
                <p className="note">Websocket status: {connectionStatus}</p>
                <p className="note">Websocket last message: {lastJsonMessage ? JSON.stringify(lastJsonMessage) : ""}</p>
            </div>
        </>
    );
}

export default App;
