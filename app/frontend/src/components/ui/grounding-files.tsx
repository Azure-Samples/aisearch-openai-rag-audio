import { AnimatePresence, motion, Variants } from "framer-motion";
import { File } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./card";
import { Button } from "./button";

type Properties = {
    files: string[];
};

const variants: Variants = {
    hidden: { opacity: 0, scale: 0.8, y: 20 },
    visible: (i: number) => ({
        opacity: 1,
        scale: 1,
        y: 0,
        transition: {
            delay: i * 0.1,
            duration: 0.3,
            type: "spring",
            stiffness: 300,
            damping: 20
        }
    })
};

export function GroundingFiles({ files }: Properties) {
    return (
        <Card className="max-w-xl md:max-w-md m-4">
            <CardHeader>
                <CardTitle>Grounding files</CardTitle>
                <CardDescription>Files used to ground the last answer.</CardDescription>
            </CardHeader>
            <CardContent className="">
                {files.length === 0 && <p>No files</p>}
                <AnimatePresence>
                    {files.length > 0 && (
                        <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: "auto" }}
                            exit={{ opacity: 0, height: 0 }}
                            transition={{ duration: 0.3 }}
                            className="h-full overflow-y-auto"
                        >
                            <div className="flex flex-wrap gap-2">
                                {files.map((file, index) => (
                                    <motion.div key={index} variants={variants} initial="hidden" animate="visible" custom={index}>
                                        <Button variant="outline" size="sm" className="rounded-full">
                                            <File className="w-4 h-4 mr-2" />
                                            {file}
                                        </Button>
                                    </motion.div>
                                ))}
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </CardContent>
        </Card>
    );
}
