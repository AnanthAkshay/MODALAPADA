import React from 'react';
import { HelpCircle, Sparkles, MapPin, Tag } from 'lucide-react';
import AudioPlayer from './AudioPlayer';

export default function AmbiguousCard({ message, best, alternatives = [] }) {
  // Combine best + alternatives up to 3 candidates
  const candidates = [];
  if (best) candidates.push(best);
  if (alternatives && alternatives.length > 0) {
    candidates.push(...alternatives.slice(0, 3 - candidates.length));
  }

  return (
    <div className="ambiguous-container">
      {/* Ambiguity Header Banner */}
      <div className="ambiguous-banner">
        <div className="banner-icon">
          <HelpCircle size={22} />
        </div>
        <div className="banner-text">
          <h3 className="banner-title">
            Multiple proverbs could fit this situation · ಬಹು ಗಾದೆಗಳು ಹೊಂದಿಕೆಯಾಗುತ್ತಿವೆ
          </h3>
          <p className="banner-desc">
            {message ||
              'Several proverbs in the oral collection closely match your description. Could you provide a bit more context or detail, or does one of the top 3 proverbs below express your intended moral?'}
          </p>
        </div>
      </div>

      {/* Top Candidates Display */}
      <div className="ambiguous-candidates">
        {candidates.map((cand, idx) => {
          const isRegionUnverified =
            !cand.region || cand.region === 'UNVERIFIED' || cand.region.trim() === '';
          const regionLabel = isRegionUnverified ? 'Region: not yet verified' : `Region: ${cand.region}`;
          const matchPercent = cand.confidence ? Math.round(cand.confidence * 100) : null;

          return (
            <div key={cand.gaade_id || idx} className="ambiguous-card">
              <div className="card-rank-badge">Option #{idx + 1}</div>

              <div className="ambiguous-card-header">
                <h4 className="ambiguous-gaade kannada-text" lang="kn">
                  {cand.gaade}
                </h4>
                {cand.audio_url && (
                  <AudioPlayer audioUrl={cand.audio_url} gaadeId={cand.gaade_id} compact={true} />
                )}
              </div>

              <div className="ambiguous-card-body">
                <p className="cand-meaning kannada-text" lang="kn">
                  <strong>ಅರ್ಥ:</strong> {cand.meaning}
                </p>
                <p className="cand-english">
                  <strong>English:</strong> {cand.english}
                </p>
              </div>

              <div className="ambiguous-card-footer">
                {cand.theme && (
                  <span className="badge badge-theme">
                    <Tag size={11} />
                    <span>{cand.theme}</span>
                  </span>
                )}
                <span className={`badge ${isRegionUnverified ? 'badge-muted' : 'badge-region'}`}>
                  <MapPin size={11} />
                  <span>{regionLabel}</span>
                </span>
                {matchPercent !== null && (
                  <span className="badge badge-confidence">
                    <Sparkles size={11} />
                    <span>Match: {matchPercent}%</span>
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

