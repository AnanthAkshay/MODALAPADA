const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

/** Resolve a server-relative media path (e.g. /api/audio/G007) against the API base. */
export function mediaUrl(path) {
  return path ? `${API_BASE}${path}` : null;
}

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, options);
  } catch (error) {
    if (error && error.name === 'AbortError') throw error;
    const failure = new Error('network');
    failure.kind = 'network';
    throw failure;
  }

  if (!response.ok) {
    const failure = new Error(`http-${response.status}`);
    failure.kind = 'http';
    failure.status = response.status;
    throw failure;
  }

  return response.json();
}

/** POST /api/match — the only place a situation is scored. */
export function matchSituation(text) {
  return request('/api/match', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, lang: 'auto' }),
  });
}

/** GET /api/gaades — filtered, paginated collection. */
export function fetchGaades({ q = '', theme = '', limit = 300, offset = 0 } = {}, signal) {
  const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  if (q) params.set('q', q);
  if (theme) params.set('theme', theme);
  return request(`/api/gaades?${params.toString()}`, { signal });
}

/** GET /api/themes — theme names with counts. */
export function fetchThemes(signal) {
  return request('/api/themes', { signal });
}

/** GET /health — used only for the quiet "unreachable" status. */
export function fetchHealth(signal) {
  return request('/health', { signal });
}
