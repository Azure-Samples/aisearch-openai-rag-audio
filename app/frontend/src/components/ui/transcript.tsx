import { AnimatePresence, motion } from "framer-motion";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./card";

type Properties = {
    transcript: string[];
};

export function Transcript({ transcript }: Properties) {
    return (
        <Card className="w-full md:max-w-md">
            <CardHeader>
                <CardTitle>Transcript</CardTitle>
                <CardDescription>Transcript of the generated audio answers.</CardDescription>
            </CardHeader>
            <CardContent className="h-[150px] md:h-[200px]">
                <AnimatePresence>
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        exit={{ opacity: 0, height: 0 }}
                        transition={{ duration: 0.3 }}
                        className="overflow-y-auto rounded-lg bg-gray-100 p-4"
                    >
                        <div className="h-full overflow-y-auto rounded-lg bg-gray-100 p-4">
                            {transcript.map(item => {
                                if (item === "\n") {
                                    return <br />;
                                }

                                return item;
                            })}
                        </div>
                    </motion.div>
                </AnimatePresence>
            </CardContent>
        </Card>
    );
}
