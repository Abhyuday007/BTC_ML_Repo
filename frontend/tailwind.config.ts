import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      fontFamily: {
        display: ["Georgia", "serif"],
        body: ["ui-sans-serif", "system-ui", "sans-serif"]
      },
      colors: {
        felt: {
          950: "#0d211b",
          900: "#133127",
          800: "#1a4334"
        },
        brass: "#d4a64f",
        coral: "#d96b4d"
      },
      boxShadow: {
        table: "0 40px 100px rgba(7, 17, 14, 0.45)"
      }
    }
  },
  plugins: []
};

export default config;
