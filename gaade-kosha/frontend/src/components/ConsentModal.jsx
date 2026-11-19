import React, { useEffect, useRef } from 'react';
import { X } from 'lucide-react';
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
              {item.name_kn}
            </span>
          </p>
          <p className="mt-0.5 text-meta text-ink-soft">{meta}</p>
        </div>

        <figure className="shrink-0">
          <img
            src={item.signatureImage}
            alt={item.altText}
            className="h-14 w-auto rounded-[6px] border border-line bg-white object-contain px-2 py-1"
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
      className="fixed inset-0 z-50 flex items-center justify-center bg-overlay p-4"
      onClick={onClose}
      role="presentation"
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="consent-title"
        onClick={(event) => event.stopPropagation()}
        className="flex max-h-[92vh] w-full max-w-[760px] flex-col overflow-hidden rounded-surface border border-line bg-paper"
      >
        <div className="flex items-start justify-between gap-4 border-b border-line px-5 py-4 sm:px-7">
          <div>
            <h2 id="consent-title" className="text-title text-indigo">
              {consentData.title.en}
            </h2>
            <p lang="kn" className="kn mt-1 text-meta text-ink-soft">
              {consentData.title.kn}
            </p>
          </div>
          <button
            ref={closeRef}
            type="button"
            onClick={onClose}
            aria-label={t('consent.close')}
            className="inline-flex h-11 w-11 shrink-0 items-center justify-center rounded-control text-ink-soft transition-colors hover:bg-paper-deep hover:text-ink"
          >
            <X size={20} strokeWidth={1.75} aria-hidden="true" />
          </button>
        </div>

        <div className="overflow-y-auto px-5 py-6 sm:px-7">
          <p className="text-body text-ink">{consentData.summaryLine.en}</p>
          <p lang="kn" className="kn mt-1 text-meta text-ink-soft">
            {consentData.summaryLine.kn}
          </p>
          <p className="mt-3 text-meta text-ink-soft">
            {consentData.institution.en} · {consentData.dateOfConsent}
          </p>

          <section className="mt-8">
            <h3 className="text-body font-semibold text-ink">
              {consentData.contributorsGroup.title.en}
            </h3>
            <p className="mt-2 border-l-2 border-turmeric pl-4 text-meta leading-[1.7] text-ink-soft">
              {consentData.contributorsGroup.declaration.en}
            </p>
            <p
              lang="kn"
              className="kn mt-2 border-l-2 border-turmeric pl-4 text-meta text-ink-soft"
            >
              {consentData.contributorsGroup.declaration.kn}
            </p>

            <ul className="mt-4 border-t border-line">
              {consentData.contributorsGroup.items.map((item) => (
                <Signatory
                  key={item.id}
                  item={item}
                  meta={`${item.relationship} · ${item.place} · ${item.gaadeCount} gaades (${item.gaadeRange})`}
                />
              ))}
            </ul>
          </section>

          <section className="mt-10">
            <h3 className="text-body font-semibold text-ink">
              {consentData.developersGroup.title.en}
            </h3>
            <p className="mt-2 border-l-2 border-turmeric pl-4 text-meta leading-[1.7] text-ink-soft">
              {consentData.developersGroup.declaration.en}
            </p>
            <p
              lang="kn"
              className="kn mt-2 border-l-2 border-turmeric pl-4 text-meta text-ink-soft"
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
      </div>
    </div>
  );
}
