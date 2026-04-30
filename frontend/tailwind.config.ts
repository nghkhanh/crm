import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        canvas: "#f3f4f6",
        panel: "#ffffff",
        ink: "#111827",
        mute: "#6b7280",
        line: "#e5e7eb",
        brand: "#1f4fbf",
        success: "#15803d",
        danger: "#b91c1c",
        warning: "#b45309"
      },
      boxShadow: {
        soft: "0 10px 30px rgba(17, 24, 39, 0.06)"
      },
      fontFamily: {
        sans: ["ui-sans-serif", "system-ui", "sans-serif"]
      }
    }
  },
  plugins: []
};

export default config;

