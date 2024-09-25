import useWebSocket from "react-use-websocket";

type Message = {
    event: string;
    data: string;
    type?: "text" | "audio";
    transcript?: string;
    message?: {
        content: {
            text: string;
        }[];
    };
};

type Parameters = {
    aoaiEndpointOverride?: string | null;
    aoaiApiKey?: string | null;

    onWebSocketOpen?: () => void;
    onWebSocketClose?: () => void;
    onWebSocketError?: (event: Event) => void;
    onWebSocketMessage?: (event: MessageEvent<any>) => void;

    onReceivedStartSession?: (message: Message) => void;
    onReceivedAddMessage?: (message: Message) => void;
    onReceivedAddContent?: (message: Message) => void;
    onReceivedInputTranscribed?: (message: Message) => void;
    onReceivedGenerationCanceled?: (message: Message) => void;
    onReceivedGenerationFinished?: (message: Message) => void;
    onReceivedVadSpeechStarted?: (message: Message) => void;
    onReceivedVadSpeechStopped?: (message: Message) => void;
    onReceivedError?: (message: Message) => void;
};

export default function useRealTime({
    aoaiEndpointOverride,
    aoaiApiKey,
    onWebSocketOpen,
    onWebSocketClose,
    onWebSocketError,
    onWebSocketMessage,
    onReceivedStartSession,
    onReceivedAddMessage,
    onReceivedAddContent,
    onReceivedInputTranscribed,
    onReceivedGenerationCanceled,
    onReceivedGenerationFinished,
    onReceivedVadSpeechStarted,
    onReceivedVadSpeechStopped,
    onReceivedError
}: Parameters) {
    const { sendJsonMessage } = useWebSocket(`${aoaiEndpointOverride ?? ""}/realtime?api-key=${aoaiApiKey}&api-version=alpha`, {
        onOpen: () => onWebSocketOpen?.(),
        onClose: () => onWebSocketClose?.(),
        onError: event => onWebSocketError?.(event),
        onMessage: event => onMessageReceived(event)
    });

    const startSession = () => {
        sendJsonMessage({
            event: "update_session_config",
            data: {
                turn_detection: "server_vad"
            }
        });

        sendJsonMessage({
            event: "update_conversation_config"
        });
    };

    const addUserAudio = (base64Audio: string) => {
        sendJsonMessage({
            event: "add_user_audio",
            data: base64Audio
        });
    };

    const onMessageReceived = (event: MessageEvent<any>) => {
        onWebSocketMessage?.(event);

        let message;
        try {
            message = JSON.parse(event.data);
        } catch (e) {
            console.error("Failed to parse JSON message:", e);
            throw e;
        }

        switch (message.event) {
            case "start_session":
                onReceivedStartSession?.(message);
                break;
            case "add_message":
                onReceivedAddMessage?.(message);
                break;
            case "add_content":
                onReceivedAddContent?.(message);
                break;
            case "input_transcribed":
                onReceivedInputTranscribed?.(message);
                break;
            case "generation_canceled":
                onReceivedGenerationCanceled?.(message);
                break;
            case "generation_finished":
                onReceivedGenerationFinished?.(message);
                break;
            case "vad_speech_started":
                onReceivedVadSpeechStarted?.(message);
                break;
            case "vad_speech_stopped":
                onReceivedVadSpeechStopped?.(message);
                break;
            case "error":
                onReceivedError?.(message);
                break;
        }
    };

    return { startSession, addUserAudio };
}
