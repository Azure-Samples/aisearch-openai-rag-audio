export type GroundingFile = {
    name: string;
    content: string;
    url: string;
};

export type HistoryItem = {
    id: string;
    answer: string;
    groundingFiles: GroundingFile[];
};

export type SessionUpdateCommand = {
    type: "session.update";
    session: {
        turn_detection?: {
            type: "server_vad" | "none";
        };
    };
};

export type InputAudioBufferAppendCommand = {
    type: "input_audio_buffer.append";
    audio: string;
};

export type InputAudioBufferClearCommand = {
    type: "input_audio_buffer.clear";
};

export type Message = {
    type: string;
};

export type ResponseAudioDelta = {
    type: "response.audio.delta";
    delta: string;
};

export type ResponseAudioTranscriptDelta = {
    type: "response.audio_transcript.delta";
    delta: string;
};

export type ResponseDone = {
    type: "response.done";
    event_id: string;
    response: {
        id: string;
        output: { id: string; content?: { transcript: string; type: string }[] }[];
    };
};
