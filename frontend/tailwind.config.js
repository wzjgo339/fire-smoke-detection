/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        fire: { DEFAULT: "#EF4444", light: "#FCA5A5", dark: "#B91C1C" },
        smoke: { DEFAULT: "#F97316", light: "#FDBA74", dark: "#C2410C" },
      },
      fontFamily: {
        sans: ['"Inter"', '"Noto Sans SC"', "system-ui", "sans-serif"],
        mono: ['"JetBrains Mono"', "monospace"],
      },
    },
  },
  plugins: [],
};
