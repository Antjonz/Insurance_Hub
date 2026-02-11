/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#EBF5FB',
          100: '#D6EAF8',
          200: '#AED6F1',
          300: '#85C1E9',
          400: '#5DADE2',
          500: '#2E86C1',
          600: '#2874A6',
          700: '#1B4F72',
          800: '#154360',
          900: '#0E2F44',
        },
        accent: {
          50: '#FEF9E7',
          100: '#FCF3CF',
          400: '#F4D03F',
          500: '#F1C40F',
          600: '#D4AC0D',
        },
      },
    },
  },
  plugins: [],
};
