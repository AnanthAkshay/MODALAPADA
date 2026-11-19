import React, { useEffect, useRef, useState } from 'react';
import { AlertCircle, Pause, Play, VolumeX } from 'lucide-react';
import { mediaUrl } from '../lib/api';
import { useCopy } from '../i18n';
import { btnIcon, btnPrimary } from '../lib/ui';
import Waveform from './Waveform';

/**
 * Elder recording player. The audio is the real human WAV served by
 * GET /api/audio/{gaade_id}. Gaades without a recording (audio_url === null,
 * e.g. G251 and G252) get a plain sentence instead of a broken player.
 */
export default function AudioPlayer({ audioUrl, gaadeId, variant = 'primary', withWaveform = false }) {
  const { t, sub, other } = useCopy();
  const [playing, setPlaying] = useState(false);
  const [failed, setFailed] = useState(false);
  const audioRef = useRef(null);
  const source = mediaUrl(audioUrl);

  useEffect(() => {
    setPlaying(false);
    setFailed(false);
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
  }, [source]);

  useEffect(() => {
    const handleStop = () => {
      if (audioRef.current && !audioRef.current.paused) {
        audioRef.current.pause();
        setPlaying(false);
      }
    };
    window.addEventListener('gaade:stop-playback', handleStop);
    return () => {
      window.removeEventListener('gaade:stop-playback', handleStop);
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, []);

  const toggle = () => {
    if (!source) return;
    window.dispatchEvent(new CustomEvent('gaade:stop-recording'));

    if (!audioRef.current) {
      const audio = new Audio(source);
      audio.onended = () => setPlaying(false);
      audio.onerror = () => {
        setPlaying(false);
        setFailed(true);
      };
      audioRef.current = audio;
    }

    if (playing) {
      audioRef.current.pause();
      setPlaying(false);
      return;
    }

    audioRef.current
      .play()
      .then(() => {
        setPlaying(true);
        setFailed(false);
      })
      .catch(() => {
        setPlaying(false);
        setFailed(true);
      });
  };

  if (!source) {
    return (
      <p className="inline-flex min-h-[44px] items-center gap-2 text-meta text-ink">
        <VolumeX size={18} strokeWidth={1.75} aria-hidden="true" className="shrink-0" />
        <span lang="kn" className="kn leading-[1.7]">
          {t('result.noRecording')}
        </span>
      </p>
    );
  }

  if (failed) {
    return (
      <p role="status" className="inline-flex min-h-[44px] flex-wrap items-center gap-x-2 gap-y-1 text-meta text-ink">
        <AlertCircle size={18} strokeWidth={1.75} aria-hidden="true" className="shrink-0 text-kumkum" />
        <span lang="kn" className="kn leading-[1.7]">
          {t('result.recordingFailed')}
        </span>
        <button
          type="button"
          onClick={toggle}
          className="min-h-[32px] text-indigo underline underline-offset-4"
        >
          <span lang="kn">{t('result.retryAudio')}</span>
        </button>
      </p>
    );
  }

  if (variant === 'quiet') {
    return (
      <span className="inline-flex items-center gap-2 text-ink">
        <button
          type="button"
          onClick={toggle}
          aria-label={`${t('result.listen')} · ${gaadeId}`}
          className={btnIcon}
        >
          {playing ? (
            <Pause size={18} strokeWidth={1.75} aria-hidden="true" />
          ) : (
            <Play size={18} strokeWidth={1.75} aria-hidden="true" />
          )}
        </button>
        {withWaveform ? <Waveform playing={playing} className="text-indigo" /> : null}
      </span>
    );
  }

  return (
    <button
      type="button"
      onClick={toggle}
      aria-label={`${playing ? t('result.pause') : t('result.listen')} · ${gaadeId}`}
      className={`${btnPrimary} flex-col gap-0 px-5 py-2`}
    >
      <span className="flex items-center gap-2">
        {playing ? (
          <Pause size={18} strokeWidth={1.75} aria-hidden="true" />
        ) : (
          <Play size={18} strokeWidth={1.75} aria-hidden="true" />
        )}
        <span lang="kn" className="kn leading-tight">
          {playing ? t('result.pause') : t('result.listen')}
        </span>
        <Waveform playing={playing} />
      </span>
      <span lang={other} className="text-[0.8em] leading-tight text-on-kumkum">
        {playing ? sub('result.pause') : sub('result.listen')}
      </span>
    </button>
  );
}
