/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      boxShadow: {
        soft: '0 18px 45px -24px rgba(15, 23, 42, 0.28)',
      },
    },
  },
  plugins: [],
}

