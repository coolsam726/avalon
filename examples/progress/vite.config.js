import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";
import { resolve } from "node:path";

export default defineConfig({
  plugins: [tailwindcss()],
  build: {
    outDir: "public/build",
    emptyOutDir: true,
    manifest: true,
    rollupOptions: {
      input: {
        app: resolve("resources/js/app.js"),
        css: resolve("resources/css/app.css"),
      },
    },
  },
  server: {
    origin: "http://127.0.0.1:5173",
  },
});
