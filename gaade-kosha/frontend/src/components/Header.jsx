import React from 'react';
import { BookOpen, CheckCircle2, AlertCircle, Volume2, VolumeX } from 'lucide-react';

export default function Header({ backendHealth, autoPlay = false, onToggleAutoPlay = null }) {
  const isHealthy = backendHealth?.status === 'healthy';

  return (
    <header className="app-header">
      <div className="header-top-row">
        <div className="header-brand">
          <div className="header-logo-badge">
            <BookOpen size={24} />
          </div>
          <div className="header-titles">
            <h1 className="header-title kannada-text" lang="kn">
              ಗಾದೆ ಕೋಶ · Gaade Kosha
            </h1>
            <p className="header-subtitle">
              Proverbs for Every Situation • Modalapada 2.0 (Dept of CSE&E, Ramaiah Institute of Technology)
            </p>
          </div>
        </div>

        <div className="header-meta">
          <div className="header-meta-row">
            <div
              className={`status-pill ${isHealthy ? 'status-ok' : 'status-err'}`}
              title={backendHealth?.message || 'Backend connection'}
            >
              {isHealthy ? <CheckCircle2 size={13} /> : <AlertCircle size={13} />}
              <span>
                {isHealthy ? `Backend Connected (${backendHealth?.gaades_count || 226} Gaades)` : 'Offline'}
              </span>
            </div>

            {onToggleAutoPlay && (
              <button
                type="button"
                className={`autoplay-toggle-btn ${autoPlay ? 'active' : ''}`}
                onClick={onToggleAutoPlay}
                aria-pressed={autoPlay}
                title="Toggle automatic playback of recorded human gaade when a match is found"
              >
                {autoPlay ? <Volume2 size={12} /> : <VolumeX size={12} />}
                <span>Auto-play Gaade: {autoPlay ? 'ON' : 'OFF'}</span>
              </button>
            )}
          </div>

          <div className="conjunct-verification-badge kannada-text" title="Verified conjunct rendering: ksha, tta, sta">
            ಲಿಪಿ ಪರಿಶೀಲನೆ: <strong>ಕ್ಷ</strong> • <strong>ತ್ತ</strong> • <strong>ಸ್ತ</strong>
          </div>
        </div>
      </div>
    </header>
  );
}

