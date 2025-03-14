import { useEffect, useRef, useState, memo } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { X } from "lucide-react";
import { useTranslation } from "react-i18next";

import { Button } from "./button";
import GroundingFile from "./grounding-file";

import { GroundingFile as GroundingFileType, HistoryItem } from "@/types";

type Properties = {
    history: HistoryItem[];
    show: boolean;
    onClosed: () => void;
    onSelectedGroundingFile: (file: GroundingFileType) => void;
};

const HistoryPanel = ({ show, history, onClosed, onSelectedGroundingFile }: Properties) => {
    const { t } = useTranslation();
    const historyEndRef = useRef<HTMLDivElement>(null);
    const [currentTime, setCurrentTime] = useState(new Date());

    // Scroll to the bottom whenever the history changes
    useEffect(() => {
        if (historyEndRef.current) {
            historyEndRef.current.scrollIntoView({ behavior: "smooth" });
        }
    }, [history]);

    // Update current time every second
    useEffect(() => {
        const interval = setInterval(() => {
            setCurrentTime(new Date());
        }, 1000);
        return () => clearInterval(interval);
    }, []);

    const formatTimestamp = (timestamp: Date) => {
        const options: Intl.DateTimeFormatOptions = {
            hour: "numeric",
            minute: "numeric",
            hour12: true
        };
        return new Intl.DateTimeFormat(navigator.language, options).format(timestamp);
    };

    const shouldShowTimestamp = (current: Date, next?: Date) => {
        const nextTime = next ? next.getTime() : currentTime.getTime();
        const diff = (nextTime - current.getTime()) / 1000; // Difference in seconds

        return diff > 60; // Show timestamp if more than 60 seconds have passed
    };

    const MemoizedGroundingFile = memo(GroundingFile);

    return (
        <AnimatePresence>
            {show && (
                <motion.div
                    initial={{ opacity: 0, x: "100%" }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: "100%" }}
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                    className="fixed inset-y-0 right-0 z-40 w-full overflow-y-auto bg-white shadow-lg sm:w-96"
                >
                    <div className="sticky top-0 z-10 mb-4 flex items-center justify-between bg-white px-4 py-2">
                        <h2 className="text-xl font-bold">{t("history.transcriptHistory")}</h2>
                        <Button variant="ghost" size="sm" onClick={onClosed}>
                            <X className="h-5 w-5" />
                        </Button>
                    </div>
                    <div className="p-4">
                        {history.length > 0 ? (
                            <div className="space-y-4">
                                {history.map((item, index) => {
                                    const nextItem = history[index + 1];
                                    const showTimestamp = shouldShowTimestamp(item.timestamp, nextItem ? nextItem.timestamp : undefined);
                                    return (
                                        <div key={index}>
                                            <div
                                                className={`rounded-lg p-4 shadow ${item.sender === "user" ? "ml-auto bg-blue-100 pl-4" : "bg-gray-100"}`}
                                                style={{ maxWidth: "75%" }}
                                            >
                                                <p className="text-sm text-gray-700">{item.transcript}</p>
                                                <div className="mt-2 flex flex-wrap gap-2">
                                                    {item.groundingFiles?.map((file, index) => (
                                                        <MemoizedGroundingFile key={index} value={file} onClick={() => onSelectedGroundingFile(file)} />
                                                    ))}
                                                </div>
                                            </div>
                                            {showTimestamp && <div className="mt-2 text-center text-xs text-gray-500">{formatTimestamp(item.timestamp)}</div>}
                                        </div>
                                    );
                                })}
                                <div ref={historyEndRef} />
                            </div>
                        ) : (
                            <p className="text-gray-500">{t("history.noHistory")}</p>
                        )}
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
    );
};

export default HistoryPanel;
