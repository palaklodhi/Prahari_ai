/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#0a0e1a',
        panel: '#111726',
        panel2: '#161d30',
        edge: '#1f2942',
        accent: '#38bdf8',
        saffron: '#ff9933',
        india: '#138808',
        danger: '#f43f5e',
        warn: '#fbbf24',
        good: '#34d399',
      },
      fontFamily: {
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
      },
    },
  },
  plugins: [],
}
