import { useCallback, useEffect, useRef, useState } from 'react';

// Error codes only — the copy for each lives in src/i18n/strings.js.
const ERROR_CODES = {
  'not-allowed': 'denied',
  'service-not-allowed': 'denied',
  'no-speech': 'no-speech',
  network: 'network',
  'audio-capture': 'audio-capture',
};

/**
 * Web Speech API voice input (kn-IN / en-IN).
 * The transcript is handed back to the caller, which keeps it editable.
 */
export default function useSpeechRecognition({ onTranscript }) {
  const [listening, setListening] = useState(false);
  const [lang, setLangState] = useState('kn-IN');
  const [interim, setInterim] = useState('');
  const [error, setError] = useState(null);

  const recognitionRef = useRef(null);
  const langRef = useRef(lang);
  langRef.current = lang;

  const supported =
    typeof window !== 'undefined' &&
    !!(window.SpeechRecognition || window.webkitSpeechRecognition);

  const stop = useCallback(() => {
    const recognition = recognitionRef.current;
    if (recognition) {
      try {
        recognition.stop();
      } catch (_) {
        /* already stopped */
      }
    }
    setListening(false);
    setInterim('');
  }, []);

  const start = useCallback(
    (langCode) => {
      if (!supported) {
        setError('unsupported');
        return;
      }

      // Never listen while audio is playing.
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
    },
    [onTranscript, supported],
  );

  const toggle = useCallback(() => {
    if (listening) stop();
    else start(langRef.current);
  }, [listening, start, stop]);

  const setLang = useCallback(
    (next) => {
      setLangState(next);
      langRef.current = next;
      if (listening) {
        stop();
        window.setTimeout(() => start(next), 150);
      }
    },
    [listening, start, stop],
  );

  // Other parts of the app (elder audio, machine voice) ask speech to stop.
  useEffect(() => {
    const handleStop = () => {
      const recognition = recognitionRef.current;
      if (recognition) {
        try {
          recognition.stop();
        } catch (_) {
          /* already stopped */
        }
      }
      setListening(false);
      setInterim('');
    };

    window.addEventListener('gaade:stop-recording', handleStop);
    return () => {
      window.removeEventListener('gaade:stop-recording', handleStop);
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (_) {
          /* already stopped */
        }
      }
    };
  }, []);

  return {
    supported,
    listening,
    lang,
    setLang,
    interim,
    error,
    dismissError: () => setError(null),
    toggle,
    stop,
  };
}
