/** @type {import('tailwindcss').Config} */
// Design tokens live here (and their light/dark values in src/index.css).
// Components reference these names only — no raw hex in component files.
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        paper: 'var(--paper)',
        'paper-deep': 'var(--paper-deep)',
        line: 'var(--line)',
        ink: 'var(--ink)',
        'ink-soft': 'var(--ink-soft)',
        indigo: 'var(--indigo)',
        kumkum: 'var(--kumkum)',
        'kumkum-hover': 'var(--kumkum-hover)',
        'on-kumkum': 'var(--on-kumkum)',
        turmeric: 'var(--turmeric)',
        'turmeric-wash': 'var(--turmeric-wash)',
        overlay: 'var(--overlay)',
      },
      fontFamily: {
        sans: ['Inter', '"Noto Sans Kannada"', 'system-ui', 'Segoe UI', 'sans-serif'],
        kannada: ['"Noto Sans Kannada"', 'Inter', 'system-ui', 'sans-serif'],
        serif: ['"Noto Serif Kannada"', 'Georgia', '"Times New Roman"', 'serif'],
      },
      fontSize: {
        meta: ['14px', { lineHeight: '1.55' }],
        body: ['16px', { lineHeight: '1.6' }],
        'body-lg': ['18px', { lineHeight: '1.6' }],
        title: ['24px', { lineHeight: '1.4' }],
        headline: ['clamp(44px, 7.4vw, 68px)', { lineHeight: '1.7' }],
        gaade: ['clamp(34px, 5vw, 56px)', { lineHeight: '1.7' }],
        poster: ['clamp(32px, 3.2vw, 44px)', { lineHeight: '1.7' }],
        // The home poster steps down with gaade length so the card keeps a
        // stable height and the play button never moves.
        'poster-hero': ['48px', { lineHeight: '1.7' }],
        'poster-lg': ['38px', { lineHeight: '1.7' }],
        'poster-md': ['34px', { lineHeight: '1.7' }],
        'poster-sm': ['30px', { lineHeight: '1.7' }],
      },
      borderRadius: {
        control: '12px',
        surface: '16px',
      },
      maxWidth: {
        content: '1100px',
        read: '680px',
      },
      boxShadow: {
        hairline: '0 1px 2px rgba(27, 26, 46, 0.06)',
      },
      keyframes: {
        'wave-bar': {
          '0%, 100%': { transform: 'scaleY(0.4)' },
          '50%': { transform: 'scaleY(1)' },
        },
        'mic-dot': {
          '0%, 100%': { opacity: '1', transform: 'scale(1)' },
          '50%': { opacity: '0.35', transform: 'scale(1.35)' },
        },
        'mic-ring': {
          '0%': { transform: 'scale(1)', opacity: '0.55' },
          '100%': { transform: 'scale(1.45)', opacity: '0' },
        },
        'fade-in': {
          from: { opacity: '0', transform: 'translateY(4px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: {
        'wave-bar': 'wave-bar 1.1s ease-in-out infinite',
        'mic-dot': 'mic-dot 1.2s ease-in-out infinite',
        'mic-ring': 'mic-ring 1.4s ease-out infinite',
        'fade-in': 'fade-in 240ms ease-out both',
      },
    },
  },
  plugins: [],
};
