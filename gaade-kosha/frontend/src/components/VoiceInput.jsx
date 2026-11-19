import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Globe, AlertCircle, X } from 'lucide-react';

export default function VoiceInput({ onTranscriptChange, currentText = '', disabled = false }) {
  const [isListening, setIsListening] = useState(false);
  const [selectedLang, setSelectedLang] = useState('kn-IN');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [errorMessage, setErrorMessage] = useState(null);
  const recognitionRef = useRef(null);

  // Check Web Speech API support
  const isSupported =
    typeof window !== 'undefined' &&
    !!(window.SpeechRecognition || window.webkitSpeechRecognition);

  // Listen for global stop-recording event (e.g. when human audio or TTS plays)
  useEffect(() => {
    const handleStopRecording = () => {
      if (recognitionRef.current && isListening) {
        try {
          recognitionRef.current.stop();
        } catch (_) {}
        setIsListening(false);
        setInterimTranscript('');
      }
    };

    window.addEventListener('gaade:stop-recording', handleStopRecording);
    return () => {
      window.removeEventListener('gaade:stop-recording', handleStopRecording);
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (_) {}
      }
    };
  }, [isListening]);

  const toggleLanguage = () => {
    const nextLang = selectedLang === 'kn-IN' ? 'en-IN' : 'kn-IN';
    setSelectedLang(nextLang);
    if (isListening && recognitionRef.current) {
      // Restart recognition with the new language
      recognitionRef.current.stop();
      setTimeout(() => startRecognition(nextLang), 100);
    }
  };

  const startRecognition = (langCode) => {
    if (!isSupported) {
      setErrorMessage(
        'Web Speech API is not supported in this browser. Please use Google Chrome, Microsoft Edge, or type your situation manually.'
      );
      return;
    }

    // Stop any active audio playback immediately per rule: never record and play at the same time
    window.dispatchEvent(new CustomEvent('gaade:stop-playback'));
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }

    setErrorMessage(null);
    setInterimTranscript('');

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
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
      console.warn('Speech recognition error:', event.error);
      let userMsg = 'Speech recognition error. Please try again.';

      if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
        userMsg =
          'Microphone permission was denied. Please allow microphone access in your browser settings to speak.';
      } else if (event.error === 'no-speech') {
        userMsg = 'No speech was detected. Please speak closer to your microphone.';
      } else if (event.error === 'network') {
        userMsg =
          'Network connection error during speech recognition. Ensure you are connected to the internet.';
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
      console.error('Recognition start error:', err);
      setIsListening(false);
    }
  };

  const handleToggleListening = () => {
    if (isListening) {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      setIsListening(false);
      setInterimTranscript('');
    } else {
      startRecognition(selectedLang);
    }
  };

  return (
    <div className="voice-input-wrapper">
      {/* Mic Button & Language Toggle */}
      <div className="voice-controls-row">
        <button
          type="button"
          className={`icon-btn mic-btn ${isListening ? 'listening' : ''}`}
          onClick={handleToggleListening}
          disabled={disabled}
          aria-label={
            isListening
              ? 'Stop speech recognition'
              : `Speak your situation in ${selectedLang === 'kn-IN' ? 'Kannada' : 'English'}`
          }
          title={
            isListening
              ? 'Click to stop listening'
              : `Speak in ${selectedLang === 'kn-IN' ? 'Kannada (kn-IN)' : 'English (en-IN)'}`
          }
        >
          {isListening ? <MicOff size={18} /> : <Mic size={18} />}
          {isListening && <span className="mic-pulse-ring"></span>}
        </button>

        <button
          type="button"
          className="voice-lang-toggle"
          onClick={toggleLanguage}
          disabled={disabled}
          title="Toggle speech recognition language (Kannada / English)"
          aria-label={`Current speech language: ${selectedLang}. Click to toggle.`}
        >
          <Globe size={12} />
          <span>{selectedLang === 'kn-IN' ? 'ಕನ್ನಡ' : 'English'}</span>
        </button>
      </div>

      {/* Real-time Listening Banner & Interim Transcript */}
      {isListening && (
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

