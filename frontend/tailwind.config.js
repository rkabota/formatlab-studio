/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx}',
    './src/components/**/*.{js,ts,jsx,tsx}',
    './src/app/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        'studio-bg': '#0f0f0f',
        'studio-panel': '#1a1a1a',
        'studio-border': '#333333',
        'studio-accent': '#0ea5e9',
        'studio-accent-dark': '#0284c7',
      },
      fontFamily: {
        sans: ['system-ui', 'sans-serif'],
        mono: ['Monaco', 'Courier New', 'monospace'],
      },
      spacing: {
        'panel-gap': '12px',
      },
    },
  },
  plugins: [],
};
