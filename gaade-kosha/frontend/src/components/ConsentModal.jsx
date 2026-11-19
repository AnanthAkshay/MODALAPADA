import React, { useEffect, useRef } from 'react';
import { X, ShieldCheck, BookOpen, Mic, Code2 } from 'lucide-react';
import { consentData } from '../data/consentData';
import { useCopy } from '../i18n';

function Signatory({ item, meta }) {
  return (
    <li className="border-b border-line py-4 last:border-b-0">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="min-w-0">
          <p className="text-body font-medium text-ink">
            {item.name}
            <span lang="kn" className="kn ml-2 text-meta text-ink-soft">
              ({item.name_kn})
            </span>
          </p>
          <p className="mt-0.5 text-meta text-ink-soft">{meta}</p>
        </div>

        <figure className="shrink-0">
          <img
            src={item.signatureImage}
            alt={item.altText}
            className="h-14 w-auto rounded-[6px] border border-line bg-white object-contain px-2 py-1 shadow-sm"
            loading="lazy"
          />
          <figcaption className="mt-1 text-center text-[12px] text-ink-soft">
            {item.date}
          </figcaption>
        </figure>
      </div>
    </li>
  );
}

export default function ConsentModal({ isOpen, onClose }) {
  const { t, sub, other } = useCopy();
  const closeRef = useRef(null);

  useEffect(() => {
    if (!isOpen) return undefined;
    const handleKey = (event) => {
      if (event.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKey);
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    closeRef.current?.focus();

    return () => {
      window.removeEventListener('keydown', handleKey);
      document.body.style.overflow = previousOverflow;
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="consent-title"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6"
    >
      <div
        className="fixed inset-0 bg-ink/50 backdrop-blur-sm transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />

      <div className="relative flex max-h-[90vh] w-full max-w-2xl flex-col rounded-hero border border-line bg-paper shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-line px-5 py-4 sm:px-7">
          <div className="flex items-center gap-2.5">
            <ShieldCheck size={22} className="text-turmeric" aria-hidden="true" />
            <div>
              <h2 id="consent-title" className="text-title font-bold text-ink">
                Informed Consent & Contributor Declarations
              </h2>
              <p lang="kn" className="kn text-meta text-ink-soft">
                ಮಾಹಿತಿಯುಕ್ತ ಒಪ್ಪಿಗೆ ಮತ್ತು ಕೊಡುಗೆದಾರರ ಘೋಷಣೆಗಳು
              </p>
            </div>
          </div>
          <button
            ref={closeRef}
            type="button"
            onClick={onClose}
            aria-label="Close dialog"
            className="flex h-10 w-10 items-center justify-center rounded-control text-ink-soft hover:bg-paper-deep hover:text-ink focus-visible:outline-offset-2"
          >
            <X size={20} strokeWidth={1.75} />
          </button>
        </div>

        {/* Body */}
        <div className="overflow-y-auto px-5 py-6 sm:px-7">
          {/* Summary Banner */}
          <div className="rounded-control border border-turmeric/30 bg-turmeric-wash p-4">
            <p className="text-body font-medium text-ink">{consentData.summaryLine.en}</p>
            <p lang="kn" className="kn mt-1 text-meta text-ink-soft">
              {consentData.summaryLine.kn}
            </p>
            <p className="mt-2 text-[12px] text-ink-soft">
              {consentData.institution.en} · {consentData.institution.kn} · {consentData.dateOfConsent}
            </p>
          </div>

          {/* Part A: Gaade Contributors */}
          <section className="mt-8">
            <div className="flex items-center gap-2">
              <BookOpen size={18} className="text-indigo" aria-hidden="true" />
              <h3 className="text-body font-semibold text-ink">
                {consentData.gaadeContributorsGroup.title.en}
              </h3>
            </div>
            <p lang="kn" className="kn text-meta font-medium text-ink-soft">
              {consentData.gaadeContributorsGroup.title.kn}
            </p>
            <p className="mt-2 border-l-2 border-turmeric pl-4 text-meta leading-[1.7] text-ink-soft">
              {consentData.gaadeContributorsGroup.declaration.en}
            </p>
            <p
              lang="kn"
              className="kn mt-2 border-l-2 border-turmeric pl-4 text-meta text-ink-soft"
            >
              {consentData.gaadeContributorsGroup.declaration.kn}
            </p>

            <ul className="mt-4 border-t border-line">
              {consentData.gaadeContributorsGroup.items.map((item) => (
                <Signatory
                  key={item.id}
                  item={item}
                  meta={`${item.relationship} · ${item.place} · ${item.gaadeCount} gaades (${item.gaadeRange})`}
                />
              ))}
            </ul>
          </section>

          {/* Part B: Audio / Voice Contributors */}
          <section className="mt-10">
            <div className="flex items-center gap-2">
              <Mic size={18} className="text-kumkum" aria-hidden="true" />
              <h3 className="text-body font-semibold text-ink">
                {consentData.audioContributorsGroup.title.en}
              </h3>
            </div>
            <p lang="kn" className="kn text-meta font-medium text-ink-soft">
              {consentData.audioContributorsGroup.title.kn}
            </p>
            <p className="mt-2 border-l-2 border-kumkum pl-4 text-meta leading-[1.7] text-ink-soft">
              {consentData.audioContributorsGroup.declaration.en}
            </p>
            <p
              lang="kn"
              className="kn mt-2 border-l-2 border-kumkum pl-4 text-meta text-ink-soft"
            >
              {consentData.audioContributorsGroup.declaration.kn}
            </p>

            <ul className="mt-4 border-t border-line">
              {consentData.audioContributorsGroup.items.map((item) => (
                <Signatory
                  key={item.id}
                  item={item}
                  meta={`${item.relationship} · ${item.place} · ${item.recordingsCount} recordings (${item.gaadeRange})`}
                />
              ))}
            </ul>
          </section>

          {/* Part C: App Developers */}
          <section className="mt-10">
            <div className="flex items-center gap-2">
              <Code2 size={18} className="text-indigo" aria-hidden="true" />
              <h3 className="text-body font-semibold text-ink">
                {consentData.developersGroup.title.en}
              </h3>
            </div>
            <p lang="kn" className="kn text-meta font-medium text-ink-soft">
              {consentData.developersGroup.title.kn}
            </p>
            <p className="mt-2 border-l-2 border-indigo pl-4 text-meta leading-[1.7] text-ink-soft">
              {consentData.developersGroup.declaration.en}
            </p>
            <p
              lang="kn"
              className="kn mt-2 border-l-2 border-indigo pl-4 text-meta text-ink-soft"
            >
              {consentData.developersGroup.declaration.kn}
            </p>

            <ul className="mt-4 border-t border-line">
              {consentData.developersGroup.items.map((item) => (
                <Signatory
                  key={item.id}
                  item={item}
                  meta={`${item.role} · ${item.place}`}
                />
              ))}
            </ul>
          </section>

          <p className="mt-8 flex flex-col text-meta text-ink-soft">
            <span lang="kn" className="kn leading-[1.7]">
              {t('consent.note')}
            </span>
            <span lang={other} className="mt-1 text-[0.8em] leading-[1.6]">
              {sub('consent.note')}
            </span>
          </p>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end border-t border-line px-5 py-4 sm:px-7">
          <button
            type="button"
            onClick={onClose}
            className="rounded-control bg-paper-deep px-4 py-2 text-body font-medium text-ink hover:bg-line focus-visible:outline-offset-2"
          >
            Close / ಮುಚ್ಚಿರಿ
          </button>
        </div>
      </div>
    </div>
  );
}
