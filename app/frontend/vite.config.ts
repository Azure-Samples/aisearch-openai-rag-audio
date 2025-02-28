import path from "path";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
import dotenv from "dotenv";

// https://vitejs.dev/config/

const outDir = process.env.VITE_BUILD_OUTDIR || "./static";
const ENV_PATH = process.env.VITE_ENV_PATH || "./.env";

dotenv.config({ path: path.resolve(__dirname, ENV_PATH) });

export default defineConfig({
    plugins: [react()],
    build: {
        outDir: outDir,
        emptyOutDir: true,
        sourcemap: true
    },
    resolve: {
        preserveSymlinks: true,
        alias: {
            "@": path.resolve(__dirname, "./src")
        }
    },
    server: {
        proxy: {
            "/api/realtime/ws": {
                target: process.env.VITE_WS_TARGET || "ws://localhost:8765",
                ws: true,
                rewriteWsOrigin: true
            }
        }
    }
});
