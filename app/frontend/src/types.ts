export type GroundingFile = {
    name: string;
    content: string;
    url: string;
};

export type SessionUpdateCommand = {
    type: "session.update";
    session: {
        voice?: "alloy" | "shimmer" | "echo";
        input_audio_format?: "pcm16" | "g711_ulaw" | "g711_alaw";
        output_audio_format?: "pcm16" | "g711_ulaw" | "g711_alaw";
        turn_detection?: {
            type: "server_vad" | "none";
            threshold?: number;
            prefix_padding_ms?: number;
            silence_duration_ms?: number;
        };
        temperature?: number;
        max_response_output_tokens?: number;
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
