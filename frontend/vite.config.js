import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // en dev, /api est renvoye vers Flask : pas de souci de CORS ni d'URL absolue
    proxy: {
      "/api": { target: "http://localhost:5000", changeOrigin: true },
    },
  },
});
