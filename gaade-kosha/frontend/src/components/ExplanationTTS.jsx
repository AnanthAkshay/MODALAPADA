import React, { useState, useEffect } from 'react';
import { Volume2, Square } from 'lucide-react';

export default function ExplanationTTS({ text }) {
  const [hasKannadaVoice, setHasKannadaVoice] = useState(false);
  const [kannadaVoice, setKannadaVoice] = useState(null);
  const [isSpeaking, setIsSpeaking] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined' || !window.speechSynthesis) {
      setHasKannadaVoice(false);
      return;
    }

    const checkVoices = () => {
      const voices = window.speechSynthesis.getVoices();
      const knVoice = voices.find(
        (v) =>
          v.lang === 'kn-IN' ||
          v.lang.toLowerCase().startsWith('kn') ||
          v.name.toLowerCase().includes('kannada')
      );

      if (knVoice) {
        setHasKannadaVoice(true);
        setKannadaVoice(knVoice);
      } else {
        setHasKannadaVoice(false);
        setKannadaVoice(null);
      }
    };

    checkVoices();
    window.speechSynthesis.onvoiceschanged = checkVoices;

    // Listen for global stop events (e.g. when human gaade audio or mic starts)
    const handleStop = () => {
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
      setIsSpeaking(false);
    };

    window.addEventListener('gaade:stop-playback', handleStop);

    return () => {
      window.removeEventListener('gaade:stop-playback', handleStop);
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  // Per Task 4: "with a Kannada voice if one exists; otherwise hide the button."
  if (!hasKannadaVoice || !text) {
    return null;
  }

  const handleToggleSpeak = () => {
    if (!window.speechSynthesis) return;

    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      return;
    }

    // Stop active audio recording and gaade audio before speaking
    window.dispatchEvent(new CustomEvent('gaade:stop-playback'));
    window.dispatchEvent(new CustomEvent('gaade:stop-recording'));

    const utterance = new SpeechSynthesisUtterance(text);
    if (kannadaVoice) {
      utterance.voice = kannadaVoice;
      utterance.lang = kannadaVoice.lang;
    }
    utterance.rate = 0.95;

    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    window.speechSynthesis.speak(utterance);
    setIsSpeaking(true);
  };

  return (
    <div className="explanation-tts-wrapper">
      <button
        type="button"
        className={`tts-btn ${isSpeaking ? 'speaking' : ''}`}
        onClick={handleToggleSpeak}
        aria-label="Listen to explanation using machine synthetic voice"
        title="Spoken explanation using browser synthetic speech"
      >
        {isSpeaking ? <Square size={13} /> : <Volume2 size={13} />}
        <span>
          {isSpeaking
            ? 'ವಿವರಣೆ ನಿಲ್ಲಿಸಿ (Stop machine voice)'
            : 'Listen to explanation (machine voice)'}
        </span>
      </button>
      <span className="tts-disclaimer-pill" title="Synthetic speech, not elder human voice">
        ಕಂಪ್ಯೂಟರ್ ಧ್ವನಿ (machine voice)
      </span>
    </div>
  );
}

