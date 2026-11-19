const STORAGE_KEY = 'gaade_theme';

function storedTheme() {
  try {
    const value = localStorage.getItem(STORAGE_KEY);
    return value === 'light' || value === 'dark' ? value : null;
  } catch (_) {
    return null;
  }
}

/**
 * Default to LIGHT theme on first visit (do not follow OS dark mode preference).
 * If the user has explicitly chosen light or dark, use that preference.
 */
export function readTheme() {
  return storedTheme() || 'light';
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
