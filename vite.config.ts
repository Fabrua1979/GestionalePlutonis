import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";
import { viteSourceLocator } from "@metagptx/vite-plugin-source-locator";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    port: 3000,
    watch: { usePolling: true, interval: 600},
  },
  plugins: [
    viteSourceLocator({
      include: ["src/pages/slides/*.tsx", "src/pages/slides/*.ts"],
      prefix: "mgx",
    }),
    react({
      babel: {
        plugins: [
          [
            "@babel/plugin-proposal-decorators",
            { legacy: true }, // Note: legacy mode must be used with TS together
          ],
        ],
      },
    }),
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));
