import { useCallback, useEffect, useRef, useState } from 'react';
import { determineAsrRoute } from '../utils/asrRouter';
import { API_BASE } from '../lib/api';

// Error codes mapped to i18n keys in src/i18n/strings.js
const ERROR_CODES = {
  'not-allowed': 'denied',
  'service-not-allowed': 'denied',
  'no-speech': 'no-speech',
  network: 'network',
  'audio-capture': 'audio-capture',
};

/**
 * Resilient Dual-Mode Speech Recognition Hook
 * 1. Primary: Native in-browser Web Speech API for Chrome / Edge
 * 2. Fallback: MediaRecorder + /api/transcribe (Groq Whisper / Sarvam) for Brave,
 *    privacy browsers, and network error recoveries.
 *
 * The final transcript is delivered to onTranscript() so the user can review and edit.
 */
export default function useSpeechRecognition({ onTranscript }) {
  const [listening, setListening] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [lang, setLangState] = useState('kn-IN');
  const [interim, setInterim] = useState('');
  const [error, setError] = useState(null);
  const [notice, setNotice] = useState(null);
  const [timerSeconds, setTimerSeconds] = useState(0);

  const recognitionRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerIntervalRef = useRef(null);
  const recordingStartTimeRef = useRef(null);
  const streamRef = useRef(null);

  const langRef = useRef(lang);
  langRef.current = lang;

  const hasNative =
    typeof window !== 'undefined' &&
    !!(window.SpeechRecognition || window.webkitSpeechRecognition);

  const hasMediaRecorder =
    typeof window !== 'undefined' &&
    typeof navigator !== 'undefined' &&
    !!(navigator.mediaDevices && window.MediaRecorder);

  const supported = hasNative || hasMediaRecorder;

  // Detect current ASR route
  const getActiveRoute = useCallback((lastError = null) => {
    const isBrave =
      typeof navigator !== 'undefined' &&
      !!(navigator.brave && typeof navigator.brave.isBrave === 'function');
    const sessionForced =
      typeof sessionStorage !== 'undefined' &&
      sessionStorage.getItem('gaade_asr_force_fallback') === 'true';

    return determineAsrRoute({
      hasNativeSpeech: hasNative,
      isBrave,
      sessionForceFallback: sessionForced,
      lastNativeError: lastError
    });
  }, [hasNative]);

  // Clean up recording timer
  const stopTimer = () => {
    if (timerIntervalRef.current) {
      clearInterval(timerIntervalRef.current);
      timerIntervalRef.current = null;
    }
    setTimerSeconds(0);
  };

  // Stop any active audio recording/recognition
  const stop = useCallback(() => {
    // Stop native recognition
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (_) {}
      recognitionRef.current = null;
    }

    // Stop MediaRecorder
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      try {
        mediaRecorderRef.current.stop();
      } catch (_) {}
    }

    stopTimer();
    setListening(false);
  }, []);

  // Upload recorded audio chunk to /api/transcribe
  const uploadAndTranscribe = async (audioBlob, mimeType) => {
    setIsTranscribing(true);
    setInterim('ಧ್ವನಿಯನ್ನು ಪರಿವರ್ತಿಸಲಾಗುತ್ತಿದೆ... (Transcribing audio...)');

    try {
      const formData = new FormData();
      const ext = mimeType.includes('mp4') ? 'mp4' : mimeType.includes('ogg') ? 'ogg' : 'webm';
      formData.append('file', audioBlob, `recording.${ext}`);

      const targetLang = langRef.current.startsWith('en') ? 'en' : 'kn';
      const endpoint = `${API_BASE}/api/transcribe?lang=${targetLang}`;

      const res = await fetch(endpoint, {
        method: 'POST',
        body: formData
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || `Server transcription failed (${res.status})`);
      }

      const data = await res.json();
      const text = (data.text || data.transcript || '').trim();

      if (text) {
        onTranscript(text);
        setInterim('');
        setError(null);
      } else {
        setError('no-speech');
        setInterim('');
      }
    } catch (err) {
      console.warn('Hosted ASR error:', err);
      setError('network');
      setInterim('');
    } finally {
      setIsTranscribing(false);
      setListening(false);
    }
  };

  // Start MediaRecorder Fallback
  const startMediaRecorderFallback = async () => {
    setError(null);
    setInterim('');
    audioChunksRef.current = [];

    // Stop any conflicting audio playback
    window.dispatchEvent(new CustomEvent('gaade:stop-playback'));
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      let mimeType = 'audio/webm;codecs=opus';
      if (!MediaRecorder.isTypeSupported(mimeType)) {
        mimeType = MediaRecorder.isTypeSupported('audio/mp4')
          ? 'audio/mp4'
          : MediaRecorder.isTypeSupported('audio/ogg')
          ? 'audio/ogg'
          : '';
      }

      const recorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) {
          audioChunksRef.current.push(e.data);
        }
      };

      recorder.onstop = async () => {
        // Stop audio tracks
        if (streamRef.current) {
          streamRef.current.getTracks().forEach((t) => t.stop());
          streamRef.current = null;
        }

        const duration = Date.now() - (recordingStartTimeRef.current || 0);
        if (duration < 600) {
          setError('no-speech');
          setListening(false);
          setInterim('');
          return;
        }

        const actualMime = recorder.mimeType || mimeType || 'audio/webm';
        const audioBlob = new Blob(audioChunksRef.current, { type: actualMime });
        await uploadAndTranscribe(audioBlob, actualMime);
      };

      recordingStartTimeRef.current = Date.now();
      recorder.start(250);
      setListening(true);

      // Start timer with 30s auto-stop
      let elapsed = 0;
      setTimerSeconds(0);
      timerIntervalRef.current = setInterval(() => {
        elapsed += 1;
        setTimerSeconds(elapsed);
        if (elapsed >= 30) {
          stop();
        }
      }, 1000);

    } catch (err) {
      console.warn('Microphone permission error:', err);
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        setError('denied');
      } else {
        setError('audio-capture');
      }
      setListening(false);
    }
  };

  // Start Native Web Speech API
  const startNative = (langCode) => {
    // Never listen while audio is playing
    window.dispatchEvent(new CustomEvent('gaade:stop-playback'));
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }

    setError(null);
    setInterim('');

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = langCode || langRef.current;
    recognition.interimResults = true;
    recognition.continuous = true;

    recognition.onstart = () => {
      setListening(true);
      setError(null);
    };

    recognition.onresult = (event) => {
      let finalChunk = '';
      let interimChunk = '';
      for (let i = event.resultIndex; i < event.results.length; i += 1) {
        const result = event.results[i];
        if (result.isFinal) finalChunk += result[0].transcript;
        else interimChunk += result[0].transcript;
      }
      setInterim(interimChunk);
      if (finalChunk.trim()) onTranscript(finalChunk.trim());
    };

    recognition.onerror = (event) => {
      console.warn('Native speech error:', event.error);
      const isNetwork = event.error === 'network' || event.error === 'service-not-allowed';
      if (isNetwork && hasMediaRecorder) {
        // Seamlessly switch to MediaRecorder fallback on Brave/Network error
        try {
          sessionStorage.setItem('gaade_asr_force_fallback', 'true');
        } catch (_) {}
        setNotice("Switching to audio recording mode...");
        recognition.stop();
        startMediaRecorderFallback();
        return;
      }

      setError(ERROR_CODES[event.error] || 'unknown');
      setListening(false);
      setInterim('');
    };

    recognition.onend = () => {
      setListening(false);
      setInterim('');
    };

    recognitionRef.current = recognition;
    try {
      recognition.start();
    } catch (_) {
      setListening(false);
    }
  };

  const start = useCallback(
    (langCode) => {
      if (!supported) {
        setError('unsupported');
        return;
      }

      const routeInfo = getActiveRoute();
      if (routeInfo.route === 'fallback' && hasMediaRecorder) {
        startMediaRecorderFallback();
      } else if (hasNative) {
        startNative(langCode);
      } else {
        startMediaRecorderFallback();
      }
    },
    [supported, hasNative, hasMediaRecorder, getActiveRoute]
  );

  const toggle = useCallback(() => {
    if (listening || isTranscribing) {
      stop();
    } else {
      start();
    }
  }, [listening, isTranscribing, start, stop]);

  const dismissError = useCallback(() => {
    setError(null);
    setNotice(null);
  }, []);

  const setLang = useCallback(
    (nextLang) => {
      setLangState(nextLang);
      if (listening) {
        stop();
        start(nextLang);
      }
    },
    [listening, start, stop]
  );

  useEffect(() => {
    return () => {
      stop();
    };
  }, [stop]);

  return {
    supported,
    listening: listening || isTranscribing,
    isTranscribing,
    lang,
    setLang,
    interim: isTranscribing ? 'ಧ್ವನಿಯನ್ನು ಪರಿವರ್ತಿಸಲಾಗುತ್ತಿದೆ... (Transcribing...)' : interim,
    error,
    notice,
    timerSeconds,
    dismissError,
    start,
    stop,
    toggle,
  };
}
