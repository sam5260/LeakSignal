import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        base: {
          950: "#080B10",
          900: "#0B1017",
          850: "#0F141C",
          800: "#141A23",
          700: "#1A212C",
          600: "#232B38",
          500: "#313B4B",
        },
        ink: {
          100: "#E9ECF2",
          300: "#C3CAD5",
          500: "#8A93A3",
          700: "#5B6474",
        },
        signal: "#3E8EF7",
        status: {
          normal: "#2FD3A0",
          monitor: "#F0B429",
          suspicious: "#F2803F",
          critical: "#F0466C",
        },
      },
      boxShadow: {
        panel: "0 20px 80px rgba(0,0,0,0.28)",
      },
      backgroundImage: {
        "grid-fade":
          "linear-gradient(rgba(62,142,247,0.025) 1px, transparent 1px), linear-gradient(90deg, rgba(62,142,247,0.025) 1px, transparent 1px)",
      },
    },
  },
  plugins: [],
};

export default config;
