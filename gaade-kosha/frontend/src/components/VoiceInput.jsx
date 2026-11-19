import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Mic, MicOff, Globe, AlertCircle, X, Square, Loader2, Sparkles } from 'lucide-react';
import { determineAsrRoute } from '../utils/asrRouter';

export default function VoiceInput({
  onTranscriptChange,
  currentText = '',
  disabled = false,
  apiBase: propApiBase = null
}) {
  const [isListening, setIsListening] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [selectedLang, setSelectedLang] = useState('kn-IN');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [errorMessage, setErrorMessage] = useState(null);
  const [friendlyNotice, setFriendlyNotice] = useState(null);
  
  // Track whether we should use the hosted ASR fallback
  const [useFallback, setUseFallback] = useState(false);

  const recognitionRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const recordStartTimeRef = useRef(0);
  const timerIntervalRef = useRef(null);
  const streamRef = useRef(null);

  const API_BASE = propApiBase !== null
    ? propApiBase
    : (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_BASE_URL) || '';

  // 1. Detection: Check Web Speech API support, Brave browser, and session memory
  useEffect(() => {
    let sessionForce = false;
    try {
      if (typeof window !== 'undefined' && sessionStorage.getItem('gaade_asr_force_fallback') === 'true') {
        sessionForce = true;
      }
    } catch (_) {}

    const hasNative =
      typeof window !== 'undefined' &&
      !!(window.SpeechRecognition || window.webkitSpeechRecognition);

    const initialRoute = determineAsrRoute({
      hasNativeSpeech: hasNative,
      isBrave: false,
      sessionForceFallback: sessionForce
    });

    if (initialRoute.route === 'fallback') {
      setUseFallback(true);
      return;
    }

    // Check if running inside Brave browser (Brave blocks Google's speech recognition endpoint)
    if (typeof navigator !== 'undefined' && navigator.brave && typeof navigator.brave.isBrave === 'function') {
      navigator.brave.isBrave().then((isBrave) => {
        const braveRoute = determineAsrRoute({
          hasNativeSpeech: hasNative,
          isBrave,
          sessionForceFallback: sessionForce
        });
        if (braveRoute.route === 'fallback') {
          setUseFallback(true);
          try {
            sessionStorage.setItem('gaade_asr_force_fallback', 'true');
          } catch (_) {}
        }
      }).catch(() => {});
    }
  }, []);

  // Cleanup helper for media stream & timers
  const cleanupMediaRecording = useCallback(() => {
    if (timerIntervalRef.current) {
      clearInterval(timerIntervalRef.current);
      timerIntervalRef.current = null;
    }
    if (streamRef.current) {
      try {
        streamRef.current.getTracks().forEach((t) => t.stop());
      } catch (_) {}
      streamRef.current = null;
    }
    mediaRecorderRef.current = null;
    audioChunksRef.current = [];
    setIsRecording(false);
    setRecordingDuration(0);
  }, []);

  // Listen for global stop-recording event (e.g. when proverb audio or TTS begins playing)
  useEffect(() => {
    const handleGlobalStop = () => {
      if (recognitionRef.current && isListening) {
        try {
          recognitionRef.current.stop();
        } catch (_) {}
        setIsListening(false);
        setInterimTranscript('');
      }
      if (isRecording) {
        cleanupMediaRecording();
      }
    };

    window.addEventListener('gaade:stop-recording', handleGlobalStop);
    return () => {
      window.removeEventListener('gaade:stop-recording', handleGlobalStop);
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (_) {}
      }
      cleanupMediaRecording();
    };
  }, [isListening, isRecording, cleanupMediaRecording]);

  // Language toggle between Kannada and English
  const toggleLanguage = () => {
    const nextLang = selectedLang === 'kn-IN' ? 'en-IN' : 'kn-IN';
    setSelectedLang(nextLang);
    if (isListening && recognitionRef.current) {
      recognitionRef.current.stop();
      setTimeout(() => startNativeRecognition(nextLang), 100);
    }
  };

  // Helper to determine supported audio MIME type
  const getSupportedMimeType = () => {
    if (typeof MediaRecorder === 'undefined') return '';
    const candidates = [
      'audio/webm;codecs=opus',
      'audio/webm',
      'audio/mp4',
      'audio/ogg;codecs=opus',
      'audio/ogg'
    ];
    for (const t of candidates) {
      if (MediaRecorder.isTypeSupported(t)) return t;
    }
    return '';
  };

  // --------------------------------------------------------------------------
  // Fallback ASR Path (MediaRecorder + Hosted Serverless ASR Endpoint)
  // --------------------------------------------------------------------------
  const startFallbackRecording = async () => {
    // Stop any active audio playback per global rule
    window.dispatchEvent(new CustomEvent('gaade:stop-playback'));
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }

    setErrorMessage(null);
    audioChunksRef.current = [];

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setErrorMessage("Voice input isn't working, please type your situation");
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const mimeType = getSupportedMimeType();
      const options = mimeType ? { mimeType } : undefined;
      const recorder = new MediaRecorder(stream, options);
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      recorder.onstop = async () => {
        const elapsedSec = (Date.now() - recordStartTimeRef.current) / 1000;
        
        // Stop audio tracks immediately
        if (streamRef.current) {
          try {
            streamRef.current.getTracks().forEach((t) => t.stop());
          } catch (_) {}
          streamRef.current = null;
        }

        if (timerIntervalRef.current) {
          clearInterval(timerIntervalRef.current);
          timerIntervalRef.current = null;
        }

        setIsRecording(false);
        setRecordingDuration(0);

        // Reject recordings shorter than 0.5 seconds
        if (elapsedSec < 0.5 || audioChunksRef.current.length === 0) {
          setErrorMessage('Recording was too short (< 0.5s). Please speak clearly for at least a second.');
          return;
        }

        const actualMime = mimeType || 'audio/webm';
        const blob = new Blob(audioChunksRef.current, { type: actualMime });

        // Dispatch to hosted ASR endpoint
        await uploadAndTranscribe(blob, actualMime);
      };

      recordStartTimeRef.current = Date.now();
      setRecordingDuration(0);
      setIsRecording(true);
      recorder.start(250); // Slice chunks every 250ms

      // 30-Second Maximum Recording Timer
      timerIntervalRef.current = setInterval(() => {
        const elapsed = Math.floor((Date.now() - recordStartTimeRef.current) / 1000);
        setRecordingDuration(elapsed);
        if (elapsed >= 30) {
          stopFallbackRecording();
        }
      }, 500);

    } catch (err) {
      console.warn('Microphone access error:', err);
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        setErrorMessage('Microphone access was denied. Please allow microphone permissions in your browser settings.');
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        setErrorMessage('No microphone device was detected on your computer.');
      } else {
        setErrorMessage("Voice input isn't working, please type your situation");
      }
      setIsRecording(false);
    }
  };

  const stopFallbackRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      try {
        mediaRecorderRef.current.stop();
      } catch (_) {}
    }
  };

  const uploadAndTranscribe = async (audioBlob, mimeType) => {
    setIsTranscribing(true);
    setErrorMessage(null);

    const formData = new FormData();
    const ext = mimeType.includes('mp4') ? 'mp4' : mimeType.includes('ogg') ? 'ogg' : 'webm';
    formData.append('file', audioBlob, `speech_input.${ext}`);
    formData.append('lang', selectedLang.startsWith('kn') ? 'kn' : 'en');

    try {
      const response = await fetch(`${API_BASE}/api/transcribe`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server returned status ${response.status}`);
      }

      const data = await response.json();
      const transcribedText = (data.text || data.transcript || '').trim();

      if (transcribedText) {
        // Task 5: Put text into existing input box so user can EDIT before sending
        const spacer = currentText && !currentText.endsWith(' ') ? ' ' : '';
        const updated = `${currentText}${spacer}${transcribedText}`;
        onTranscriptChange(updated);
        setFriendlyNotice(null);
      } else {
        setErrorMessage('No speech could be recognized. Please speak clearly and try again.');
      }
    } catch (err) {
      console.error('ASR Upload/Transcription Error:', err);
      // Task 6: Friendly error keeping typed input fully usable
      setErrorMessage("Voice input isn't working, please type your situation");
    } finally {
      setIsTranscribing(false);
    }
  };

  // --------------------------------------------------------------------------
  // Primary Path: Native Web Speech API (Chrome / Edge)
  // --------------------------------------------------------------------------
  const startNativeRecognition = (langCode) => {
    window.dispatchEvent(new CustomEvent('gaade:stop-playback'));
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }

    setErrorMessage(null);
    setInterimTranscript('');

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setUseFallback(true);
      startFallbackRecording();
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = langCode || selectedLang;
    recognition.interimResults = true;
    recognition.continuous = true;

    recognition.onstart = () => {
      setIsListening(true);
      setErrorMessage(null);
    };

    recognition.onresult = (event) => {
      let interim = '';
      let finalChunk = '';

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        const item = event.results[i];
        if (item.isFinal) {
          finalChunk += item[0].transcript;
        } else {
          interim += item[0].transcript;
        }
      }

      setInterimTranscript(interim);

      if (finalChunk.trim()) {
        const spacer = currentText && !currentText.endsWith(' ') ? ' ' : '';
        const updated = `${currentText}${spacer}${finalChunk.trim()}`;
        onTranscriptChange(updated);
      }
    };

    recognition.onerror = (event) => {
      console.warn('Speech recognition error event:', event.error);

      // Task 2 & 6: Automatic fallback on network or service-not-allowed errors (e.g. Brave)
      if (event.error === 'network' || event.error === 'service-not-allowed') {
        try {
          sessionStorage.setItem('gaade_asr_force_fallback', 'true');
        } catch (_) {}
        setUseFallback(true);
        setIsListening(false);
        setInterimTranscript('');
        setFriendlyNotice("Your browser's built-in speech service isn't available, switching to the recorder.");
        setTimeout(() => {
          startFallbackRecording();
        }, 200);
        return;
      }

      let userMsg = 'Speech recognition error. Please try again.';
      if (event.error === 'not-allowed') {
        userMsg = 'Microphone access was denied. Please allow microphone permissions in your browser.';
      } else if (event.error === 'no-speech') {
        userMsg = 'No speech was detected. Please speak closer to your microphone.';
      } else if (event.error === 'audio-capture') {
        userMsg = 'No microphone device was detected on your computer.';
      }

      setErrorMessage(userMsg);
      setIsListening(false);
      setInterimTranscript('');
    };

    recognition.onend = () => {
      setIsListening(false);
      setInterimTranscript('');
    };

    recognitionRef.current = recognition;

    try {
      recognition.start();
    } catch (err) {
      console.warn('Native speech recognition start failed:', err);
      setUseFallback(true);
      startFallbackRecording();
    }
  };

  const stopNativeRecognition = () => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (_) {}
    }
    setIsListening(false);
    setInterimTranscript('');
  };

  // --------------------------------------------------------------------------
  // Main Action Dispatcher
  // --------------------------------------------------------------------------
  const handleToggleVoice = () => {
    if (isRecording) {
      stopFallbackRecording();
      return;
    }
    if (isListening) {
      stopNativeRecognition();
      return;
    }

    if (useFallback) {
      startFallbackRecording();
    } else {
      startNativeRecognition(selectedLang);
    }
  };

  const activeMode = isTranscribing
    ? 'transcribing'
    : isRecording
    ? 'recording'
    : isListening
    ? 'listening'
    : 'idle';

  return (
    <div className="voice-input-wrapper">
      {/* Mic Button & Language Toggle */}
      <div className="voice-controls-row">
        <button
          type="button"
          className={`icon-btn mic-btn ${activeMode !== 'idle' ? 'listening' : ''} ${isRecording ? 'recording-active' : ''}`}
          onClick={handleToggleVoice}
          disabled={disabled || isTranscribing}
          aria-label={
            isRecording
              ? 'Stop recording and transcribe speech'
              : isListening
              ? 'Stop listening'
              : `Speak your situation in ${selectedLang === 'kn-IN' ? 'Kannada' : 'English'}`
          }
          title={
            isTranscribing
              ? 'Transcribing audio...'
              : isRecording
              ? 'Click to stop recording and transcribe'
              : isListening
              ? 'Click to stop listening'
              : `Speak in ${selectedLang === 'kn-IN' ? 'Kannada (kn-IN)' : 'English (en-IN)'}`
          }
        >
          {isTranscribing ? (
            <Loader2 size={18} className="spin-icon" />
          ) : isRecording ? (
            <Square size={16} className="stop-square" />
          ) : isListening ? (
            <MicOff size={18} />
          ) : (
            <Mic size={18} />
          )}
          {(isListening || isRecording) && <span className="mic-pulse-ring"></span>}
        </button>

        <button
          type="button"
          className="voice-lang-toggle"
          onClick={toggleLanguage}
          disabled={disabled || isRecording || isListening || isTranscribing}
          title="Toggle speech recognition language (Kannada / English)"
          aria-label={`Current speech language: ${selectedLang}. Click to toggle.`}
        >
          <Globe size={12} />
          <span>{selectedLang === 'kn-IN' ? 'ಕನ್ನಡ' : 'English'}</span>
        </button>
      </div>

      {/* Real-time Listening Banner (Native Web Speech) */}
      {isListening && !isRecording && (
        <div className="interim-transcript-banner" role="status" aria-live="polite">
          <div className="listening-indicator">
            <span className="pulsing-red-dot"></span>
            <span className="listening-text kannada-text">
              {selectedLang === 'kn-IN' ? 'ಮಾತನಾಡಿ... (Listening in Kannada)' : 'Listening in English...'}
            </span>
          </div>

          {interimTranscript && (
            <div className="interim-text-preview kannada-text">
              "{interimTranscript}"
            </div>
          )}

          <div className="editable-hint">
            ✏️ <em>You can freely edit the transcript in the input box below before sending.</em>
          </div>
        </div>
      )}

      {/* Fallback Recording Banner (MediaRecorder Active) */}
      {isRecording && (
        <div className="interim-transcript-banner recording-banner" role="status" aria-live="polite">
          <div className="listening-indicator">
            <span className="pulsing-red-dot"></span>
            <span className="listening-text kannada-text">
              {selectedLang === 'kn-IN' ? 'ಧ್ವನಿಗ್ರಹಣ ಚಾಲನೆಯಲ್ಲಿದೆ... (Recording in Kannada)' : 'Recording audio in English...'}
            </span>
            <span className="recording-timer">
              {String(Math.floor(recordingDuration / 60)).padStart(2, '0')}:
              {String(recordingDuration % 60).padStart(2, '0')} / 00:30
            </span>
          </div>

          <div className="recording-tip">
            Click the square stop button or speak for up to 30 seconds to finish.
          </div>
        </div>
      )}

      {/* Fallback Transcribing State Banner */}
      {isTranscribing && (
        <div className="interim-transcript-banner transcribing-banner" role="status" aria-live="polite">
          <div className="listening-indicator">
            <Loader2 size={16} className="spin-icon" />
            <span className="listening-text kannada-text">
              ಧ್ವನಿ ಪರಿವರ್ತಿಸಲಾಗುತ್ತಿದೆ... Transcribing spoken audio...
            </span>
          </div>
        </div>
      )}

      {/* Friendly Notice Banner (e.g. switching to recorder) */}
      {friendlyNotice && !errorMessage && (
        <div className="voice-notice-banner" role="status">
          <Sparkles size={14} className="notice-sparkle" />
          <span>{friendlyNotice}</span>
          <button
            type="button"
            className="dismiss-error-btn"
            onClick={() => setFriendlyNotice(null)}
            aria-label="Dismiss notice"
          >
            <X size={12} />
          </button>
        </div>
      )}

      {/* Error Message Alert */}
      {errorMessage && (
        <div className="voice-error-banner" role="alert">
          <AlertCircle size={15} />
          <span>{errorMessage}</span>
          <button
            type="button"
            className="dismiss-error-btn"
            onClick={() => setErrorMessage(null)}
            aria-label="Dismiss error"
          >
            <X size={13} />
          </button>
        </div>
      )}
    </div>
  );
}
