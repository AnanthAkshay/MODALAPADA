const RAW_BASE = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || '';
export const API_BASE = RAW_BASE.replace(/\/+$/, '');
const CLOUD_FALLBACK = 'https://modalapada.onrender.com';

/** Resolve a server-relative media path (e.g. /api/audio/G007) against the API base. */
export function mediaUrl(path) {
  if (!path) return null;
  if (path.startsWith('http://') || path.startsWith('https://')) return path;
  if (API_BASE) return `${API_BASE}${path}`;
  return path;
}

async function request(path, options = {}) {
  const url = `${API_BASE}${path}`;
  let response;
  try {
    response = await fetch(url, options);
  } catch (error) {
    if (error && error.name === 'AbortError') throw error;
    // If running on Vercel or custom domain with relative API_BASE and it fails,
    // retry once against the direct Render cloud backend:
    if (!API_BASE && typeof window !== 'undefined' && !window.location.hostname.includes('onrender.com')) {
      try {
        response = await fetch(`${CLOUD_FALLBACK}${path}`, options);
      } catch (fallbackErr) {
        if (fallbackErr && fallbackErr.name === 'AbortError') throw fallbackErr;
        const failure = new Error('network');
        failure.kind = 'network';
        throw failure;
      }
    } else {
      const failure = new Error('network');
      failure.kind = 'network';
      throw failure;
    }
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

/** GET /api/gaades/random — random canonical gaade with audio, with automatic fallback */
export async function fetchRandomGaade(exclude = '', signal) {
  const params = new URLSearchParams();
  if (exclude) params.set('exclude', exclude);
  const query = params.toString() ? `?${params.toString()}` : '';

  try {
    return await request(`/api/gaades/random${query}`, {
      signal,
      cache: 'no-store',
      headers: { 'Cache-Control': 'no-store' },
    });
  } catch (err) {
    if (err && err.name === 'AbortError') throw err;
    // Fallback: If Render has not updated /api/gaades/random yet (returning 400),
    // retrieve collection and pick one canonical gaade with audio:
    const data = await fetchGaades({ limit: 300 }, signal);
    const excludedSet = new Set((exclude || '').split(',').map((s) => s.trim()).filter(Boolean));
    const items = data.items || [];
    const withAudio = items.filter((x) => x.audio_url && !excludedSet.has(x.gaade_id));
    const pool = withAudio.length > 0 ? withAudio : items.filter((x) => x.audio_url);
    if (!pool.length) throw err;
    const chosen = pool[Math.floor(Math.random() * pool.length)];
    return chosen;
  }
}

/** GET /api/themes — theme names with counts. */
export function fetchThemes(signal) {
  return request('/api/themes', { signal });
}

/** GET /health — used for the status indicator dot. */
export function fetchHealth(signal) {
  return request('/health', { signal });
}
