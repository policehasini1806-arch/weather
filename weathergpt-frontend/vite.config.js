import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The backend only allows CORS from http://localhost:5173 (see
// backend/app/config/settings.py -> ALLOWED_ORIGINS), so pin the port.
// strictPort makes Vite fail loudly instead of silently moving to 5174,
// which would show up as a confusing CORS error in the browser.
export default defineConfig({
  plugins: [react()],
  server: { port: 5173, strictPort: true },
});
