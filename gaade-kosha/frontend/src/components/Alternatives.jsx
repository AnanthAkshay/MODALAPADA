import React from 'react';
import AudioPlayer from './AudioPlayer';
import { useCopy } from '../i18n';

export default function Alternatives({ items = [], onChoose, activeIndex = -1, titleKey = 'result.othersFit' }) {
  const { t, sub, other } = useCopy();
  if (!items.length) return null;

  return (
    <section className="mt-10" aria-labelledby="alternatives-heading">
      <h3 id="alternatives-heading" className="flex flex-col">
        <span lang="kn" className="kn text-meta font-semibold leading-[1.7] text-ink">
          {t(titleKey)}
        </span>
        <span lang={other} className="text-[13px] leading-tight text-ink-soft">
          {sub(titleKey)}
        </span>
      </h3>

      <ol className="mt-3 border-t border-line">
        {items.map((item, index) => (
          <li key={item.gaade_id || index} className="border-b border-line">
            <div className="flex items-center gap-4 py-4">
              <button
                type="button"
                onClick={() => onChoose(index)}
                aria-current={index === activeIndex ? 'true' : undefined}
                className="min-w-0 flex-1 rounded-control text-left"
              >
                <span lang="kn" className="kn-serif block break-words text-body-lg font-bold leading-[1.7] text-indigo">
                  {item.gaade}
                </span>
                <span className="mt-1 block truncate text-meta text-ink-soft">{item.english}</span>
              </button>
              <AudioPlayer audioUrl={item.audio_url} gaadeId={item.gaade_id} variant="quiet" />
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}
