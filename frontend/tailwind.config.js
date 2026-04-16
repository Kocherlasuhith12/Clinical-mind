/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50:  "#E1F5EE",
          100: "#9FE1CB",
          200: "#5DCAA5",
          500: "#1D9E75",
          600: "#0F6E56",
          700: "#085041",
          900: "#04342C",
        },
        emergency: {
          50:  "#FFEEEE",
          500: "#CC2222",
          700: "#991111",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
