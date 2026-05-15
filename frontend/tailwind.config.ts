import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}", "./components/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: "#172027",
        slate: "#53616b",
        mist: "#f5f7f8",
        line: "#dde4e7",
        teal: "#0d9488",
        amber: "#d97706",
        navy: "#13283b"
      },
      boxShadow: {
        panel: "0 18px 45px rgba(19, 40, 59, 0.08)"
      }
    }
  },
  plugins: []
};

export default config;
