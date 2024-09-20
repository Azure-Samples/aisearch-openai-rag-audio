import { useState } from "react";
import "./App.css";

function App() {
    const [recording, setRecording] = useState(false);

    return (
        <>
            <h1>Talk to your data</h1>
            <div className="card">
                <button className="button" onClick={() => setRecording(!recording)}>
                    {recording ? "Stop" : "Talk"}
                </button>
                <p className="note">{recording ? "Listening..." : "Press to start talking"}</p>
            </div>
        </>
    );
}

export default App;
