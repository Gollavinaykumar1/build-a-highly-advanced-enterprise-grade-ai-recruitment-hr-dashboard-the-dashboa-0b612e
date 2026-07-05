import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  base: "/build-a-highly-advanced-enterprise-grade-ai-recruitment-hr-dashboard-the-dashboa-0b612e/",
  build: { outDir: "dist", assetsDir: "assets" },
  server: { port: 3000 },
});
