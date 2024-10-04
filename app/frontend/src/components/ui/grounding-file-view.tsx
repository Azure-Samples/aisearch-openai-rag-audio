import { AnimatePresence, motion } from "framer-motion";
import { X } from "lucide-react";

import { Button } from "./button";
import { GroundingFile } from "@/types";

type Properties = {
    groundingFile: GroundingFile | null;
    onClosed: () => void;
};

export default function GroundingFileView({ groundingFile, onClosed }: Properties) {
    return (
        <AnimatePresence>
            {groundingFile && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4"
                    onClick={() => onClosed()}
                >
                    <motion.div
                        initial={{ scale: 0.9, y: 20 }}
                        animate={{ scale: 1, y: 0 }}
                        exit={{ scale: 0.9, y: 20 }}
                        className="flex max-h-[90vh] w-full max-w-2xl flex-col rounded-lg bg-white p-6"
                        onClick={e => e.stopPropagation()}
                    >
                        <div className="mb-4 flex items-center justify-between">
                            <h2 className="text-xl font-bold">{groundingFile.name}</h2>
                            <Button
                                aria-label="Close grounding file view"
                                variant="ghost"
                                size="sm"
                                className="text-gray-500 hover:text-gray-700"
                                onClick={() => onClosed()}
                            >
                                <X className="h-5 w-5" />
                            </Button>
                        </div>
                        <div className="flex-grow overflow-hidden">
                            <pre className="h-[40vh] overflow-auto text-wrap rounded-md bg-gray-100 p-4 text-sm">
                                <code>{groundingFile.content}</code>
                            </pre>
                        </div>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
