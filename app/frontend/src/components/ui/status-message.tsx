import "./status-message.css";

type Properties = {
    isRecording: boolean;
};

export default function StatusMessage({ isRecording }: Properties) {
    if (!isRecording) {
        return <p className="text mb-4 mt-6">Ask anything about about God, Life, and You</p>;
    }

    return (
        <div className="flex items-center">
            <div className="relative h-6 w-6 overflow-hidden">
                <div className="absolute inset-0 flex items-end justify-around">
                    {[...Array(4)].map((_, i) => (
                        <div
                            key={i}
                            className="w-1 rounded-full bg-purple-600 opacity-80"
                            style={{
                                animation: `barHeight${(i % 3) + 1} 1s ease-in-out infinite`,
                                animationDelay: `${i * 0.1}s`
                            }}
                        />
                    ))}
                </div>
            </div>
            <p className="text mb-4 ml-2 mt-6">Conversation in progress</p>
        </div>
    );
}
