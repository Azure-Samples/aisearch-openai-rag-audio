import { File } from "lucide-react";

import { Button } from "./button";

import { GroundingFile as GroundingFileType } from "@/types";

type Properties = {
    value: GroundingFileType;
    onClick: () => void;
};

export default function GroundingFile({ value, onClick }: Properties) {
    return (
        <Button variant="outline" size="sm" className="rounded-full" onClick={onClick}>
            <File className="mr-2 h-4 w-4" />
            {value.name}
        </Button>
    );
}
