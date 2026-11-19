import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Sparkles, MapPin, Tag, ShieldCheck, HelpCircle } from 'lucide-react';
import AudioPlayer from './AudioPlayer';
import ExplanationTTS from './ExplanationTTS';

export default function ProverbCard({ item, alternatives = [], autoPlay = false }) {
  const [showAlternatives, setShowAlternatives] = useState(false);

  if (!item) return null;

  // Region Badge logic: strictly unverified unless explicit provenance exists
  const isRegionUnverified =
    !item.region ||
    item.region === 'UNVERIFIED' ||
    item.region.trim() === '';
  const regionLabel = isRegionUnverified ? 'Region: not yet verified' : `Region: ${item.region}`;

  // Provenance Entry Status logic: never imply elder verification that hasn't happened
  const verificationStatus = item.provenance?.verification_status || 'unverified';
  const entryStatusLabel = `Entry status: ${verificationStatus}`;

  const matchPercent = item.confidence ? Math.round(item.confidence * 100) : null;

  return (
    <div className="proverb-card">
      {/* Top Badges Bar */}
      <div className="proverb-badges">
        {item.theme && (
          <span className="badge badge-theme">
            <Tag size={12} />
            <span>{item.theme}</span>
          </span>
        )}
        <span className={`badge ${isRegionUnverified ? 'badge-muted' : 'badge-region'}`}>
          <MapPin size={12} />
          <span>{regionLabel}</span>
        </span>
        <span className="badge badge-provenance" title="Source provenance record">
          <ShieldCheck size={12} />
          <span>{entryStatusLabel}</span>
        </span>
        {matchPercent !== null && (
          <span className="badge badge-confidence" title={`Algorithmic Match Score: ${item.confidence}`}>
            <Sparkles size={12} />
            <span>Match: {matchPercent}%</span>
          </span>
        )}
      </div>

      {/* Prominent Kannada Gaade Heading */}
      <div className="proverb-header-row">
        <h2 className="gaade-heading kannada-text" lang="kn">
          {item.gaade}
        </h2>
        <div className="audio-player-wrapper">
          <AudioPlayer audioUrl={item.audio_url} gaadeId={item.gaade_id} autoPlay={autoPlay} />
        </div>
      </div>

      {/* Labelled Sections */}
      <div className="proverb-sections">
        {/* Section 1: Meaning */}
        <div className="proverb-section">
          <div className="section-label">Meaning · ತಾತ್ಪರ್ಯ</div>
          <div className="section-content kannada-text" lang="kn">
            {item.meaning}
          </div>
        </div>

        {/* Section 2: English Equivalent */}
        <div className="proverb-section">
          <div className="section-label">English equivalent</div>
          <div className="section-content english-content">
            {item.english}
          </div>
        </div>

        {/* Section 3: Why it fits */}
        <div className="proverb-section highlight-section">
          <div className="section-label">Why it fits · ಸಂದರ್ಭಕ್ಕೆ ಏಕೆ ಸೂಕ್ತ?</div>
          <div className="section-content explanation-content">
            {item.explanation ||
              `This proverb applies because the described situation reflects "${item.meaning}", mirroring the timeless advice: "${item.english}".`}
          </div>
          <ExplanationTTS text={item.explanation} />
        </div>
      </div>

      {/* Collapsible "Other possible gaades" */}
      {alternatives && alternatives.length > 0 && (
        <div className="alternatives-container">
          <button
            type="button"
            className="alternatives-toggle-btn"
            onClick={() => setShowAlternatives(!showAlternatives)}
            aria-expanded={showAlternatives}
            aria-label="Toggle other possible gaades"
          >
            <span>Other possible gaades ({alternatives.length}) · ಇತರ ಸಂಭವನೀಯ ಗಾದೆಗಳು</span>
            {showAlternatives ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>

          {showAlternatives && (
            <div className="alternatives-list">
              {alternatives.map((alt, idx) => {
                const altRegionUnverified = !alt.region || alt.region === 'UNVERIFIED';
                const altMatchPercent = alt.confidence ? Math.round(alt.confidence * 100) : null;

                return (
                  <div key={alt.gaade_id || idx} className="alternative-card">
                    <div className="alt-top-row">
                      <span className="alt-gaade kannada-text" lang="kn">
                        {alt.gaade}
                      </span>
                      {alt.audio_url && (
                        <AudioPlayer audioUrl={alt.audio_url} gaadeId={alt.gaade_id} compact={true} />
                      )}
                    </div>

                    <div className="alt-details">
                      <p className="alt-meaning kannada-text">
                        <strong>ಅರ್ಥ:</strong> {alt.meaning}
                      </p>
                      <p className="alt-english">
                        <strong>English:</strong> {alt.english}
                      </p>
                    </div>

                    <div className="alt-badges">
                      {alt.theme && <span className="alt-badge">{alt.theme}</span>}
                      <span className="alt-badge muted">
                        {altRegionUnverified ? 'Region: not yet verified' : alt.region}
                      </span>
                      {altMatchPercent !== null && (
                        <span className="alt-badge score">Score: {altMatchPercent}%</span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

