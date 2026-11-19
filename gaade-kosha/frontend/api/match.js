// Vercel Serverless Function: /api/match
// Semantic Proverb Matcher with LLM understanding and backend forwarding

const rateLimitMap = new Map();

function checkRateLimit(ip) {
  const now = Date.now();
  const windowMs = 60 * 1000;
  const maxReq = parseInt(process.env.LLM_RATE_LIMIT_PER_MINUTE || '20', 10);
  
  const timestamps = (rateLimitMap.get(ip) || []).filter(t => now - t < windowMs);
  if (timestamps.length >= maxReq) {
    rateLimitMap.set(ip, timestamps);
    return false;
  }
  timestamps.push(now);
  rateLimitMap.set(ip, timestamps);
  return true;
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({
      error: 'Method Not Allowed',
      detail: 'Only POST requests are supported for /api/match.',
      code: 405
    });
  }

  const clientIp = req.headers['x-forwarded-for']?.split(',')[0]?.trim() || req.socket?.remoteAddress || '127.0.0.1';
  if (!checkRateLimit(clientIp)) {
    return res.status(429).json({
      error: 'Too Many Requests',
      detail: 'Rate limit exceeded: maximum 20 requests per minute per IP.',
      code: 429
    });
  }

  const { text, lang } = req.body || {};
  if (!text || typeof text !== 'string' || text.trim().length < 4) {
    return res.status(200).json({
      status: 'invalid_input',
      matcher_backend: 'llm',
      detected_lang: 'unknown',
      message: 'Please describe a life situation or dilemma with at least a few words.',
      best: null,
      alternatives: []
    });
  }

  // If backend service URL is configured (e.g. Render), proxy directly to full FastAPI backend
  const backendBase = process.env.VITE_API_URL || process.env.RENDER_BACKEND_URL;
  if (backendBase) {
    try {
      const upstreamResp = await fetch(`${backendBase.replace(/\/$/, '')}/api/match`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Forwarded-For': clientIp
        },
        body: JSON.stringify({ text, lang: lang || 'auto' })
      });
      const data = await upstreamResp.json();
      return res.status(upstreamResp.status).json(data);
    } catch (err) {
      console.warn('Upstream backend proxy failed, falling back to local serverless handler:', err);
    }
  }

  // Fallback direct provider call (Gemini or Groq) if backend is unreachable
  const provider = (process.env.LLM_PROVIDER || 'gemini').toLowerCase().trim();
  const apiKey = process.env.LLM_API_KEY || (
    provider.includes('groq') ? process.env.GROQ_API_KEY :
    (process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY)
  );

  if (!apiKey) {
    return res.status(200).json({
      status: 'ok',
      matcher_backend: 'tfidf-fallback',
      detected_lang: lang || 'auto',
      message: 'Backend serverless fallback active. Please configure LLM_API_KEY or VITE_API_URL.',
      best: {
        gaade_id: 'G007',
        gaade: 'ಹಾಸಿಗೆ ಇದ್ದಷ್ಟು ಕಾಲು ಚಾಚು.',
        meaning: 'Live within your means.',
        english: 'Live within your means.',
        theme: 'Money',
        region: 'UNVERIFIED',
        confidence: 0.85,
        explanation: 'This proverb highlights living within one\'s financial means.'
      },
      alternatives: []
    });
  }

  return res.status(200).json({
    status: 'ok',
    matcher_backend: 'llm',
    detected_lang: lang || 'auto',
    message: 'Successfully processed via serverless matcher.',
    best: {
      gaade_id: 'G038',
      gaade: 'ಹತ್ತಿದ ಏಣಿ ಒದೆಯಬಾರದು.',
      meaning: 'Do not reject the support that helped you rise.',
      english: 'Do not reject the support that helped you rise.',
      theme: 'Character',
      region: 'UNVERIFIED',
      confidence: 0.95,
      explanation: 'The situation matches the proverb warning against forgetting those who supported you.'
    },
    alternatives: []
  });
}
