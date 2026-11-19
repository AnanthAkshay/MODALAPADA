import React, { useEffect } from 'react';
import { X, ShieldCheck, Users, FileSignature, MapPin, Calendar, BookOpen, CheckCircle2, Mic } from 'lucide-react';
import { consentData } from '../data/consentData';

export default function ConsentModal({ isOpen, onClose }) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="modal-backdrop"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="consent-modal-title"
    >
      <div
        className="consent-modal-card"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Top Header */}
        <div className="consent-modal-header">
          <div className="consent-header-left">
            <div className="consent-icon-badge">
              <ShieldCheck size={24} />
            </div>
            <div>
              <h2 id="consent-modal-title" className="consent-header-title">
                {consentData.title.en}
              </h2>
              <p className="consent-header-subtitle kannada-text" lang="kn">
                {consentData.title.kn}
              </p>
            </div>
          </div>
          <button
            type="button"
            className="consent-close-btn"
            onClick={onClose}
            aria-label="Close consent declaration modal"
            title="Close (Esc)"
          >
            <X size={20} />
          </button>
        </div>

        {/* Modal Body */}
        <div className="consent-modal-body">
          {/* Summary Banner */}
          <div className="consent-summary-banner">
            <div className="summary-left">
              <div className="summary-headline">
                <CheckCircle2 size={20} className="summary-icon" />
                <span className="summary-text-en">{consentData.summaryLine.en}</span>
              </div>
              <div className="summary-text-kn kannada-text" lang="kn">
                {consentData.summaryLine.kn}
              </div>
            </div>
            <div className="summary-meta">
              <span className="summary-date-badge">
                <Calendar size={13} />
                <span>Date: {consentData.dateOfConsent}</span>
              </span>
              <span className="summary-inst-badge">
                Modalapada 2.0 • RIT CSE&E
              </span>
            </div>
          </div>

          {/* Part A: Gaade Contributors (Total 250 Gaade) */}
          <section className="consent-section" aria-labelledby="gaade-contributors-heading">
            <div className="consent-section-header">
              <div className="section-title-wrap">
                <BookOpen size={18} className="section-icon" />
                <h3 id="gaade-contributors-heading" className="section-title">
                  {consentData.gaadeContributorsGroup.title.en}
                </h3>
              </div>
              <div className="section-title-kn kannada-text" lang="kn">
                {consentData.gaadeContributorsGroup.title.kn}
              </div>
            </div>

            {/* Formal Declaration Paragraph */}
            <div className="consent-declaration-box">
              <p className="declaration-text-en">
                <strong>Declaration:</strong> {consentData.gaadeContributorsGroup.declaration.en}
              </p>
              <p className="declaration-text-kn kannada-text" lang="kn">
                <strong>ಘೋಷಣೆ:</strong> {consentData.gaadeContributorsGroup.declaration.kn}
              </p>
            </div>

            {/* Gaade Contributors Cards Grid */}
            <div className="consent-cards-grid">
              {consentData.gaadeContributorsGroup.items.map((contributor) => (
                <div key={contributor.id} className="contributor-card">
                  <div className="card-top-row">
                    <div className="contributor-num">#{contributor.id}</div>
                    <div className="gaade-count-badge">
                      <strong>{contributor.gaadeCount}</strong> Gaades ({contributor.gaadeRange})
                    </div>
                  </div>

                  <div className="card-identity">
                    <h4 className="contributor-name">
                      {contributor.name}
                      <span className="contributor-name-kn kannada-text" lang="kn">
                        ({contributor.name_kn})
                      </span>
                    </h4>
                    <p className="contributor-role">
                      <span>{contributor.relationship}</span> •{' '}
                      <span className="kannada-text" lang="kn">{contributor.relationship_kn}</span>
                    </p>
                  </div>

                  <div className="card-meta-row">
                    <span className="meta-pill">
                      <MapPin size={13} />
                      <span>{contributor.place} ({contributor.place_kn})</span>
                    </span>
                    <span className="meta-pill">
                      <Calendar size={13} />
                      <span>{contributor.date}</span>
                    </span>
                  </div>

                  {/* Signature Box */}
                  <div className="signature-container">
                    <div className="signature-label">
                      <FileSignature size={12} />
                      <span>Verified Signature</span>
                    </div>
                    <div className="signature-image-wrapper">
                      <img
                        src={contributor.signatureImage}
                        alt={contributor.altText}
                        className="signature-image"
                        loading="lazy"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Part B: Audio / Voice Contributors (Total 250 Recordings) */}
          <section className="consent-section" aria-labelledby="audio-contributors-heading">
            <div className="consent-section-header">
              <div className="section-title-wrap">
                <Mic size={18} className="section-icon" />
                <h3 id="audio-contributors-heading" className="section-title">
                  {consentData.audioContributorsGroup.title.en}
                </h3>
              </div>
              <div className="section-title-kn kannada-text" lang="kn">
                {consentData.audioContributorsGroup.title.kn}
              </div>
            </div>

            {/* Formal Declaration Paragraph */}
            <div className="consent-declaration-box">
              <p className="declaration-text-en">
                <strong>Audio Consent:</strong> {consentData.audioContributorsGroup.declaration.en}
              </p>
              <p className="declaration-text-kn kannada-text" lang="kn">
                <strong>ಧ್ವನಿ ಒಪ್ಪಿಗೆ ಘೋಷಣೆ:</strong> {consentData.audioContributorsGroup.declaration.kn}
              </p>
            </div>

            {/* Audio Contributors Cards Grid */}
            <div className="consent-cards-grid">
              {consentData.audioContributorsGroup.items.map((voice) => (
                <div key={voice.id} className="contributor-card audio-card">
                  <div className="card-top-row">
                    <div className="contributor-num">#{voice.id}</div>
                    <div className="gaade-count-badge audio-count-badge">
                      <strong>{voice.recordingCount}</strong> Recordings ({voice.audioRange})
                    </div>
                  </div>

                  <div className="card-identity">
                    <h4 className="contributor-name">
                      {voice.name}
                      <span className="contributor-name-kn kannada-text" lang="kn">
                        ({voice.name_kn})
                      </span>
                    </h4>
                    <p className="contributor-role">
                      <span>{voice.relationship}</span> •{' '}
                      <span className="kannada-text" lang="kn">{voice.relationship_kn}</span>
                    </p>
                  </div>

                  <div className="card-meta-row">
                    <span className="meta-pill">
                      <MapPin size={13} />
                      <span>{voice.place} ({voice.place_kn})</span>
                    </span>
                    <span className="meta-pill">
                      <Calendar size={13} />
                      <span>{voice.date}</span>
                    </span>
                  </div>

                  {/* Signature Box */}
                  <div className="signature-container">
                    <div className="signature-label">
                      <FileSignature size={12} />
                      <span>Verified Signature</span>
                    </div>
                    <div className="signature-image-wrapper">
                      <img
                        src={voice.signatureImage}
                        alt={voice.altText}
                        className="signature-image"
                        loading="lazy"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Part C: App Developers */}
          <section className="consent-section" aria-labelledby="developers-heading">
            <div className="consent-section-header">
              <div className="section-title-wrap">
                <Users size={18} className="section-icon" />
                <h3 id="developers-heading" className="section-title">
                  {consentData.developersGroup.title.en}
                </h3>
              </div>
              <div className="section-title-kn kannada-text" lang="kn">
                {consentData.developersGroup.title.kn}
              </div>
            </div>

            {/* Formal Declaration Paragraph */}
            <div className="consent-declaration-box">
              <p className="declaration-text-en">
                <strong>Authorization:</strong> {consentData.developersGroup.declaration.en}
              </p>
              <p className="declaration-text-kn kannada-text" lang="kn">
                <strong>ದೃಢೀಕರಣ:</strong> {consentData.developersGroup.declaration.kn}
              </p>
            </div>

            {/* Developers Cards Grid */}
            <div className="consent-cards-grid developers-grid">
              {consentData.developersGroup.items.map((dev) => (
                <div key={dev.id} className="contributor-card dev-card">
                  <div className="card-top-row">
                    <div className="contributor-num">#{dev.id}</div>
                    <div className="dev-role-badge">
                      <span>{dev.role}</span>
                    </div>
                  </div>

                  <div className="card-identity">
                    <h4 className="contributor-name">
                      {dev.name}
                      <span className="contributor-name-kn kannada-text" lang="kn">
                        ({dev.name_kn})
                      </span>
                    </h4>
                    <p className="contributor-role kannada-text" lang="kn">
                      {dev.role_kn}
                    </p>
                  </div>

                  <div className="card-meta-row">
                    <span className="meta-pill">
                      <MapPin size={13} />
                      <span>{dev.place} ({dev.place === 'Bengaluru' ? 'ಬೆಂಗಳೂರು' : dev.place})</span>
                    </span>
                    <span className="meta-pill">
                      <Calendar size={13} />
                      <span>{dev.date}</span>
                    </span>
                  </div>

                  {/* Signature Box */}
                  <div className="signature-container">
                    <div className="signature-label">
                      <FileSignature size={12} />
                      <span>Verified Signature</span>
                    </div>
                    <div className="signature-image-wrapper">
                      <img
                        src={dev.signatureImage}
                        alt={dev.altText}
                        className="signature-image"
                        loading="lazy"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>

        {/* Modal Footer */}
        <div className="consent-modal-footer">
          <p className="footer-inst-note kannada-text" lang="kn">
            {consentData.institution.kn}
          </p>
          <button
            type="button"
            className="consent-confirm-btn"
            onClick={onClose}
          >
            Close / ಮುಚ್ಚಿರಿ
          </button>
        </div>
      </div>
    </div>
  );
}
