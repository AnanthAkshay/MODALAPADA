// Vercel Serverless Function: /api/transcribe
// Hosted ASR endpoint supporting groq-whisper (default), sarvam, and google

const rateLimitMap = new Map();

function checkRateLimit(ip) {
  const now = Date.now();
  const windowMs = 60 * 1000;
  const maxReq = parseInt(process.env.ASR_RATE_LIMIT_PER_MINUTE || '20', 10);
  
  const timestamps = (rateLimitMap.get(ip) || []).filter(t => now - t < windowMs);
  if (timestamps.length >= maxReq) {
    rateLimitMap.set(ip, timestamps);
    return false;
  }
  timestamps.push(now);
  rateLimitMap.set(ip, timestamps);
  return true;
}

export const config = {
  api: {
    bodyParser: false, // Disables body parsing to allow streaming / multipart
  },
};

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method Not Allowed', detail: 'Only POST requests are supported.', code: 405 });
  }

  // 1. Rate Limiting Check (20 req/min/IP)
  const clientIp = req.headers['x-forwarded-for']?.split(',')[0]?.trim() || req.socket?.remoteAddress || '127.0.0.1';
  if (!checkRateLimit(clientIp)) {
    return res.status(429).json({
      error: 'Too Many Requests',
      detail: 'Rate limit exceeded: maximum 20 audio transcription requests per minute per IP.',
      code: 429
    });
  }

  // 2. Read Raw Request Body with 5MB size limit
  const maxBytes = parseInt(process.env.ASR_MAX_FILE_SIZE_BYTES || String(5 * 1024 * 1024), 10);
  const chunks = [];
  let totalSize = 0;

  try {
    for await (const chunk of req) {
      totalSize += chunk.length;
      if (totalSize > maxBytes) {
        return res.status(413).json({
          error: 'Payload Too Large',
          detail: 'Audio recording exceeds the 5 MB limit. Please record a shorter clip.',
          code: 413
        });
      }
      chunks.push(chunk);
    }
  } catch (err) {
    return res.status(400).json({ error: 'Bad Request', detail: 'Failed reading audio upload stream.', code: 400 });
  }

  const rawBuffer = Buffer.concat(chunks);
  if (rawBuffer.length < 100) {
    return res.status(400).json({ error: 'Bad Request', detail: 'Audio file payload is empty or too short.', code: 400 });
  }

  // 3. Provider & Key Configuration
  const provider = (process.env.ASR_PROVIDER || 'groq-whisper').toLowerCase().trim();
  const apiKey = process.env.ASR_API_KEY || (
    provider.includes('groq') ? process.env.GROQ_API_KEY :
    provider.includes('sarvam') ? process.env.SARVAM_API_KEY :
    process.env.GOOGLE_API_KEY
  );

  if (!apiKey) {
    return res.status(401).json({
      error: 'Unauthorized',
      detail: `ASR provider '${provider}' API key is not configured in Vercel environment variables. Please set ASR_API_KEY or GROQ_API_KEY.`,
      code: 401
    });
  }

  const contentType = req.headers['content-type'] || 'audio/webm';
  const lang = req.query.lang?.toString().toLowerCase().startsWith('kn') ? 'kn' : 'kn';

  // 4. Forward to Upstream Hosted ASR with 20s timeout
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 20000);

  try {
    if (provider === 'groq-whisper' || provider === 'groq') {
      // Groq Whisper API
      const groqFormData = new FormData();
      const ext = contentType.includes('mp4') ? 'mp4' : (contentType.includes('ogg') ? 'ogg' : 'webm');
      groqFormData.append('file', new Blob([rawBuffer], { type: contentType }), `speech.${ext}`);
      groqFormData.append('model', 'whisper-large-v3');
      groqFormData.append('language', lang);
      groqFormData.append('response_format', 'json');

      const groqResp = await fetch('https://api.groq.com/openai/v1/audio/transcriptions', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${apiKey}` },
        body: groqFormData,
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!groqResp.ok) {
        const errText = await groqResp.text();
        return res.status(502).json({ error: 'Bad Gateway', detail: `Groq ASR error (${groqResp.status}): ${errText.slice(0, 200)}`, code: 502 });
      }

      const groqData = await groqResp.json();
      return res.status(200).json({
        status: 'success',
        text: (groqData.text || '').trim(),
        transcript: (groqData.text || '').trim(),
        provider: 'groq-whisper',
        language: lang
      });

    } else if (provider === 'sarvam') {
      // Sarvam AI API
      const sarvamFormData = new FormData();
      sarvamFormData.append('file', new Blob([rawBuffer], { type: contentType }), 'speech.wav');
      sarvamFormData.append('model', 'saaras:v1');
      sarvamFormData.append('language_code', lang === 'kn' ? 'kn-IN' : 'en-IN');

      const sarvamResp = await fetch('https://api.sarvam.ai/speech-to-text', {
        method: 'POST',
        headers: { 'api-subscription-key': apiKey },
        body: sarvamFormData,
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!sarvamResp.ok) {
        const errText = await sarvamResp.text();
        return res.status(502).json({ error: 'Bad Gateway', detail: `Sarvam ASR error (${sarvamResp.status}): ${errText.slice(0, 200)}`, code: 502 });
      }

      const sarvamData = await sarvamResp.json();
      const text = sarvamData.transcript || sarvamData.text || '';
      return res.status(200).json({
        status: 'success',
        text: text.trim(),
        transcript: text.trim(),
        provider: 'sarvam',
        language: lang
      });

    } else {
      clearTimeout(timeoutId);
      return res.status(400).json({
        error: 'Bad Request',
        detail: `Unsupported provider '${provider}'. Supported: 'groq-whisper', 'sarvam'.`,
        code: 400
      });
    }

  } catch (err) {
    clearTimeout(timeoutId);
    if (err.name === 'AbortError') {
      return res.status(504).json({ error: 'Gateway Timeout', detail: 'ASR request timed out after 20 seconds.', code: 504 });
    }
    return res.status(502).json({ error: 'Bad Gateway', detail: `Failed connecting to ASR provider: ${err.message}`, code: 502 });
  }
}
