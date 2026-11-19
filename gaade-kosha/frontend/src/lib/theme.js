const STORAGE_KEY = 'gaade_theme';

function storedTheme() {
  try {
    const value = localStorage.getItem(STORAGE_KEY);
    return value === 'light' || value === 'dark' ? value : null;
  } catch (_) {
    return null;
  }
}

function systemTheme() {
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

export function readTheme() {
  return storedTheme() || systemTheme();
}

export function applyTheme(theme, { persist = true } = {}) {
  const root = document.documentElement;
  root.dataset.theme = theme;
  root.style.colorScheme = theme;
  if (persist) {
    try {
      localStorage.setItem(STORAGE_KEY, theme);
    } catch (_) {
      /* storage unavailable — the session still renders */
    }
  }
}

/** Follow the OS setting until the user picks a theme themselves. */
export function watchSystemTheme(onChange) {
  const query = window.matchMedia('(prefers-color-scheme: dark)');
  const handle = (event) => {
    if (storedTheme()) return;
    onChange(event.matches ? 'dark' : 'light');
  };
  query.addEventListener('change', handle);
  return () => query.removeEventListener('change', handle);
}
