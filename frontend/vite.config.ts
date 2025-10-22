import tailwindcss from "@tailwindcss/vite";
import basicSsl from "@vitejs/plugin-basic-ssl";
import react from "@vitejs/plugin-react";
import type { PluginOption } from "vite";
import { defineConfig } from "vite";
import path from "path";

export default defineConfig(() => {
  const enableHttps = process.env.VITE_ENABLE_HTTPS !== "false";
  const proxyTarget = process.env.VITE_PROXY_TARGET ?? "https://localhost";

  const plugins: PluginOption[] = [tailwindcss(), react()];
  if (enableHttps) {
    plugins.push(basicSsl());
  }

  return {
    plugins,
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src")
      }
    },
    server: {
      https: enableHttps ? {} : false,
      proxy: {
        "/api": {
          target: proxyTarget,
          changeOrigin: true,
          secure: false,
          followRedirects: true
        }
      }
    },
    preview: {
      https: enableHttps ? {} : false
    }
  };
});
