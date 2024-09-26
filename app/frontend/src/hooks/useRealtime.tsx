import useWebSocket from "react-use-websocket";

import {
    InputAudioBufferAppendCommand,
    InputAudioBufferClearCommand,
    Message,
    ResponseAudioDelta,
    ResponseAudioTranscriptDelta,
    ResponseDone,
    SessionUpdateCommand
} from "@/types";

type Parameters = {
    aoaiEndpointOverride?: string | null;
    aoaiApiKey?: string | null;

    onWebSocketOpen?: () => void;
    onWebSocketClose?: () => void;
    onWebSocketError?: (event: Event) => void;
    onWebSocketMessage?: (event: MessageEvent<any>) => void;

    onReceivedSessionCreated?: (message: Message) => void;
    onReceivedItemCreated?: (message: Message) => void;
    onReceivedItemDeleted?: (message: Message) => void;
    onReceivedItemTruncated?: (message: Message) => void;
    onReceivedResponseCreated?: (message: Message) => void;
    onReceivedResponseDone?: (message: ResponseDone) => void;
    onReceivedResponseCancelled?: (message: Message) => void;
    onReceivedRateLimitsUpdated?: (message: Message) => void;
    onReceivedResponseOutputItemAdded?: (message: Message) => void;
    onReceivedResponseOutputItemDone?: (message: Message) => void;
    onReceivedResponseContentPartAdded?: (message: Message) => void;
    onReceivedResponseContentPartDone?: (message: Message) => void;
    onReceivedResponseAudioDelta?: (message: ResponseAudioDelta) => void;
    onReceivedResponseAudioDone?: (message: Message) => void;
    onReceivedResponseAudioTranscriptDelta?: (message: ResponseAudioTranscriptDelta) => void;
    onReceivedResponseAudioTranscriptDone?: (message: Message) => void;
    onReceivedResponseTextDelta?: (message: Message) => void;
    onReceivedResponseTextDone?: (message: Message) => void;
    onReceivedResponseFunctionCallArgumentsDelta?: (message: Message) => void;
    onReceivedResponseFunctionCallArgumentsDone?: (message: Message) => void;
    onReceivedInputAudioBufferSpeechStarted?: (message: Message) => void;
    onReceivedInputAudioBufferSpeechStopped?: (message: Message) => void;
    onReceivedItemInputAudioTranscriptionCompleted?: (message: Message) => void;
    onReceivedItemInputAudioTranscriptionFailed?: (message: Message) => void;
    onReceivedInputAudioBufferCommitted?: (message: Message) => void;
    onReceivedInputAudioBufferCleared?: (message: Message) => void;
    onReceivedError?: (message: Message) => void;
};

export default function useRealTime({
    aoaiEndpointOverride,
    aoaiApiKey,
    onWebSocketOpen,
    onWebSocketClose,
    onWebSocketError,
    onWebSocketMessage,
    onReceivedSessionCreated,
    onReceivedItemCreated,
    onReceivedItemDeleted,
    onReceivedItemTruncated,
    onReceivedResponseCreated,
    onReceivedResponseDone,
    onReceivedResponseCancelled,
    onReceivedRateLimitsUpdated,
    onReceivedResponseOutputItemAdded,
    onReceivedResponseOutputItemDone,
    onReceivedResponseContentPartAdded,
    onReceivedResponseContentPartDone,
    onReceivedResponseAudioDelta,
    onReceivedResponseAudioDone,
    onReceivedResponseAudioTranscriptDelta,
    onReceivedResponseAudioTranscriptDone,
    onReceivedResponseTextDelta,
    onReceivedResponseTextDone,
    onReceivedResponseFunctionCallArgumentsDelta,
    onReceivedResponseFunctionCallArgumentsDone,
    onReceivedInputAudioBufferSpeechStarted,
    onReceivedInputAudioBufferSpeechStopped,
    onReceivedItemInputAudioTranscriptionCompleted,
    onReceivedItemInputAudioTranscriptionFailed,
    onReceivedInputAudioBufferCommitted,
    onReceivedInputAudioBufferCleared,
    onReceivedError
}: Parameters) {
    const { sendJsonMessage } = useWebSocket(`${aoaiEndpointOverride ?? ""}/realtime?api-key=${aoaiApiKey}&api-version=alpha`, {
        onOpen: () => onWebSocketOpen?.(),
        onClose: () => onWebSocketClose?.(),
        onError: event => onWebSocketError?.(event),
        onMessage: event => onMessageReceived(event)
    });

    // TODO: Remove? Start ws?
    const startSession = () => {
        const command: SessionUpdateCommand = {
            type: "session.update",
            session: {
                turn_detection: {
                    type: "server_vad"
                }
            }
        };

        sendJsonMessage(command);
    };

    const addUserAudio = (base64Audio: string) => {
        const command: InputAudioBufferAppendCommand = {
            type: "input_audio_buffer.append",
            audio: base64Audio
        };

        sendJsonMessage(command);
    };

    const inputAudioBufferClear = () => {
        const command: InputAudioBufferClearCommand = {
            type: "input_audio_buffer.clear"
        };

        sendJsonMessage(command);
    };

    const onMessageReceived = (event: MessageEvent<any>) => {
        onWebSocketMessage?.(event);

        let message: Message;
        try {
            message = JSON.parse(event.data);
        } catch (e) {
            console.error("Failed to parse JSON message:", e);
            throw e;
        }

        switch (message.type) {
            case "session_created":
                onReceivedSessionCreated?.(message);
                break;
            case "item_created":
                onReceivedItemCreated?.(message);
                break;
            case "item_deleted":
                onReceivedItemDeleted?.(message);
                break;
            case "item_truncated":
                onReceivedItemTruncated?.(message);
                break;
            case "response_created":
                onReceivedResponseCreated?.(message);
                break;
            case "response.done":
                onReceivedResponseDone?.(message as ResponseDone);
                break;
            case "response_cancelled":
                onReceivedResponseCancelled?.(message);
                break;
            case "rate_limits_updated":
                onReceivedRateLimitsUpdated?.(message);
                break;
            case "response_output_item_added":
                onReceivedResponseOutputItemAdded?.(message);
                break;
            case "response_output_item_done":
                onReceivedResponseOutputItemDone?.(message);
                break;
            case "response_content_part_added":
                onReceivedResponseContentPartAdded?.(message);
                break;
            case "response_content_part_done":
                onReceivedResponseContentPartDone?.(message);
                break;
            case "response.audio.delta":
                onReceivedResponseAudioDelta?.(message as ResponseAudioDelta);
                break;
            case "response.audio.done":
                onReceivedResponseAudioDone?.(message);
                break;
            case "response.audio_transcript.delta":
                onReceivedResponseAudioTranscriptDelta?.(message as ResponseAudioTranscriptDelta);
                break;
            case "response_audio_transcript_done":
                onReceivedResponseAudioTranscriptDone?.(message);
                break;
            case "response_text_delta":
                onReceivedResponseTextDelta?.(message);
                break;
            case "response_text_done":
                onReceivedResponseTextDone?.(message);
                break;
            case "response_function_call_arguments_delta":
                onReceivedResponseFunctionCallArgumentsDelta?.(message);
                break;
            case "response_function_call_arguments_done":
                onReceivedResponseFunctionCallArgumentsDone?.(message);
                break;
            case "input_audio_buffer_speech_started":
                onReceivedInputAudioBufferSpeechStarted?.(message);
                break;
            case "input_audio_buffer_speech_stopped":
                onReceivedInputAudioBufferSpeechStopped?.(message);
                break;
            case "item_input_audio_transcription_completed":
                onReceivedItemInputAudioTranscriptionCompleted?.(message);
                break;
            case "item_input_audio_transcription_failed":
                onReceivedItemInputAudioTranscriptionFailed?.(message);
                break;
            case "input_audio_buffer_committed":
                onReceivedInputAudioBufferCommitted?.(message);
                break;
            case "input_audio_buffer_cleared":
                onReceivedInputAudioBufferCleared?.(message);
                break;
            case "error":
                onReceivedError?.(message);
                break;
        }
    };

    return { startSession, addUserAudio, inputAudioBufferClear };
}
