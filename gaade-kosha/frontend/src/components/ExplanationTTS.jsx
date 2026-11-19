import React, { useEffect, useState } from 'react';
import { Square, Volume2 } from 'lucide-react';
import { useCopy } from '../i18n';
import { btnSecondary } from '../lib/ui';

/**
 * Synthetic "machine voice" reading of the explanation via speechSynthesis.
 * Shown only when the browser actually has a Kannada voice, and always
 * labelled — it is never presented as an elder's recording.
 */
export default function ExplanationTTS({ text }) {
  const { t, sub, other } = useCopy();
  const [voice, setVoice] = useState(null);
  const [speaking, setSpeaking] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined' || !window.speechSynthesis) return undefined;

    const pickVoice = () => {
      const voices = window.speechSynthesis.getVoices();
      const kannada = voices.find(
        (candidate) =>
          candidate.lang === 'kn-IN' ||
          candidate.lang.toLowerCase().startsWith('kn') ||
          candidate.name.toLowerCase().includes('kannada'),
      );
      setVoice(kannada || null);
    };

    pickVoice();
    window.speechSynthesis.onvoiceschanged = pickVoice;

    const handleStop = () => {
      window.speechSynthesis.cancel();
      setSpeaking(false);
    };
    window.addEventListener('gaade:stop-playback', handleStop);

    return () => {
      window.removeEventListener('gaade:stop-playback', handleStop);
      window.speechSynthesis.cancel();
    };
  }, []);

  if (!voice || !text) return null;

  const toggle = () => {
    if (!window.speechSynthesis) return;

    if (speaking) {
      window.speechSynthesis.cancel();
      setSpeaking(false);
      return;
    }

    window.dispatchEvent(new CustomEvent('gaade:stop-playback'));
    window.dispatchEvent(new CustomEvent('gaade:stop-recording'));

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.voice = voice;
    utterance.lang = voice.lang;
    utterance.rate = 0.95;
    utterance.onend = () => setSpeaking(false);
    utterance.onerror = () => setSpeaking(false);

    window.speechSynthesis.speak(utterance);
    setSpeaking(true);
  };

  return (
    <div className="inline-flex flex-wrap items-center gap-x-3 gap-y-1">
      <button
        type="button"
        onClick={toggle}
        aria-pressed={speaking}
        aria-label={`${speaking ? t('result.stopReading') : t('result.readExplanation')} · ${t('result.machineVoice')}`}
        className={`${btnSecondary} flex-col gap-0 px-4 py-2`}
      >
        <span className="flex items-center gap-2">
          {speaking ? (
            <Square size={16} strokeWidth={1.75} aria-hidden="true" />
          ) : (
            <Volume2 size={18} strokeWidth={1.75} aria-hidden="true" />
          )}
          <span lang="kn" className="kn leading-tight">
            {speaking ? t('result.stopReading') : t('result.readExplanation')}
          </span>
        </span>
        <span lang={other} className="text-[0.8em] leading-tight text-ink-soft">
          {speaking ? sub('result.stopReading') : sub('result.readExplanation')}
        </span>
      </button>

      <span className="flex flex-col text-meta text-ink-soft">
        <span lang="kn" className="kn leading-[1.7]">
          {t('result.machineVoice')}
        </span>
        <span lang={other} className="text-[0.8em] leading-tight">
          {sub('result.machineVoice')}
        </span>
      </span>
    </div>
  );
}
