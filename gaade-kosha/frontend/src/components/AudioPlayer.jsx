import React, { useState, useRef, useEffect } from 'react';
import { Play, Pause, Square, RotateCcw, Volume2, AlertCircle } from 'lucide-react';

export default function AudioPlayer({
  audioUrl,
  gaadeId,
  compact = false,
  autoPlay = false,
  onPlayStart = null
}) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [isFinished, setIsFinished] = useState(false);
  const [autoplayBlocked, setAutoplayBlocked] = useState(false);
  const audioRef = useRef(null);

  const API_BASE = import.meta.env.VITE_API_BASE_URL || '';
  const resolvedUrl = audioUrl ? `${API_BASE}${audioUrl}` : null;

  // Listen for global stop events (e.g. when microphone starts recording)
  useEffect(() => {
    const handleStopAll = () => {
      if (audioRef.current && isPlaying) {
        audioRef.current.pause();
        setIsPlaying(false);
      }
    };
    window.addEventListener('gaade:stop-playback', handleStopAll);
    return () => {
      window.removeEventListener('gaade:stop-playback', handleStopAll);
    };
  }, [isPlaying]);

  useEffect(() => {
    // Reset state if audioUrl changes
    setIsPlaying(false);
    setHasError(false);
    setIsFinished(false);
    setAutoplayBlocked(false);

    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }

    if (resolvedUrl && autoPlay) {
      const audio = new Audio(resolvedUrl);
      audio.onended = () => {
        setIsPlaying(false);
        setIsFinished(true);
      };
      audio.onerror = () => {
        setIsPlaying(false);
        setHasError(true);
      };
      audioRef.current = audio;

      // Autoplay attempt (handle browser policy block)
      if (onPlayStart) onPlayStart();
      audio
        .play()
        .then(() => {
          setIsPlaying(true);
          setAutoplayBlocked(false);
        })
        .catch((err) => {
          // Browser prevented autoplay without prior gesture
          console.info('Autoplay deferred by browser policy:', err);
          setIsPlaying(false);
          setAutoplayBlocked(true);
        });
    }

    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, [resolvedUrl, autoPlay]);

  const initAudioIfNeeded = () => {
    if (!audioRef.current && resolvedUrl) {
      const audio = new Audio(resolvedUrl);
      audio.onended = () => {
        setIsPlaying(false);
        setIsFinished(true);
      };
      audio.onerror = () => {
        setIsPlaying(false);
        setHasError(true);
      };
      audioRef.current = audio;
    }
  };

  const handlePlay = () => {
    if (!resolvedUrl) {
      setHasError(true);
      return;
    }

    // Stop active recording if any
    window.dispatchEvent(new CustomEvent('gaade:stop-recording'));

    initAudioIfNeeded();
    if (onPlayStart) onPlayStart();

    audioRef.current
      .play()
      .then(() => {
        setIsPlaying(true);
        setIsFinished(false);
        setAutoplayBlocked(false);
      })
      .catch((err) => {
        console.warn('Audio playback error:', err);
        setIsPlaying(false);
        setHasError(true);
      });
  };

  const handleStop = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
      setIsFinished(false);
    }
  };

  const handleReplay = () => {
    if (!resolvedUrl) return;
    initAudioIfNeeded();
    window.dispatchEvent(new CustomEvent('gaade:stop-recording'));
    audioRef.current.currentTime = 0;
    audioRef.current
      .play()
      .then(() => {
        setIsPlaying(true);
        setIsFinished(false);
      })
      .catch(() => {
        setIsPlaying(false);
        setHasError(true);
      });
  };

  if (!audioUrl) {
    return (
      <span className="audio-pill disabled" title="Audio recording not available for this proverb">
        <Volume2 size={compact ? 13 : 15} />
        <span>ಧ್ವನಿ ಲಭ್ಯವಿಲ್ಲ (No Audio)</span>
      </span>
    );
  }

  if (hasError) {
    return (
      <span className="audio-pill error" title="Human audio recording could not be loaded">
        <AlertCircle size={compact ? 13 : 15} />
        <span>ಧ್ವನಿ ದೋಷ (Audio Unavailable)</span>
      </span>
    );
  }

  return (
    <div className={`audio-player-controls ${compact ? 'compact' : ''}`}>
      {!isPlaying ? (
        <button
          type="button"
          className={`audio-btn ${compact ? 'compact' : ''}`}
          onClick={isFinished ? handleReplay : handlePlay}
          aria-label={isFinished ? `Replay audio for ${gaadeId}` : `Play original human recording for ${gaadeId}`}
          title={isFinished ? 'Replay original human recording' : 'Play authentic human recording'}
        >
          {isFinished ? <RotateCcw size={compact ? 13 : 16} /> : <Play size={compact ? 13 : 16} />}
          <span>{isFinished ? 'ಮತ್ತೊಮ್ಮೆ ಆಲಿಸಿ (Replay)' : 'ಗಾದೆ ಆಲಿಸಿ (Play Gaade)'}</span>
        </button>
      ) : (
        <div className="audio-active-group">
          <button
            type="button"
            className="audio-btn playing active"
            onClick={handleStop}
            aria-label={`Stop recording playback for ${gaadeId}`}
            title="Stop audio playback"
          >
            <Square size={compact ? 12 : 14} />
            <span>ನಿಲ್ಲಿಸಿ (Stop)</span>
            <span className="audio-wave-bars">
              <span></span>
              <span></span>
              <span></span>
            </span>
          </button>
        </div>
      )}

      {autoplayBlocked && (
        <span className="autoplay-blocked-hint" title="Browser blocked autoplay policy">
          ▶ Auto-play blocked by browser. Click to listen.
        </span>
      )}
    </div>
  );
}
