import React, { useRef } from 'react';
import SituationForm from './SituationForm';
import GaadePoster from './GaadePoster';
import { EXAMPLES } from '../data/examples';
import { useCopy } from '../i18n';

export default function HomeScreen({ inputValue, onInputChange, onSubmit, speech }) {
  const { t, sub } = useCopy();
  const inputRef = useRef(null);

  return (
    <main id="main" className="mx-auto w-full max-w-content px-4 pb-16 pt-10 sm:px-8 sm:pt-16">
      <div className="grid items-start gap-12 lg:grid-cols-[minmax(0,1fr)_384px] lg:gap-14">
        <div className="min-w-0">
          <h1
            lang="kn"
            className="kn-serif break-words text-headline font-bold leading-[1.7] text-indigo wrap-balance"
          >
            {t('home.headline')}
          </h1>

          <p lang="kn" className="kn mt-4 max-w-[28ch] break-words text-body-lg leading-[1.7] text-ink">
            {t('home.subline')}
          </p>
          <p lang="en" className="mt-1 max-w-[44ch] text-meta leading-[1.6] text-ink-soft">
            {sub('home.subline')}
          </p>

          <SituationForm
            inputRef={inputRef}
            value={inputValue}
            onChange={onInputChange}
            onSubmit={onSubmit}
            speech={speech}
          />

          <div className="mt-10">
            <p lang="kn" className="kn text-meta leading-[1.7] text-ink">
              {t('home.examples')}
            </p>
            <p lang="en" className="text-[13px] leading-tight text-ink-soft">
              {sub('home.examples')}
            </p>

            <ul className="mt-3 flex flex-wrap gap-2">
              {EXAMPLES.map((example) => (
                <li key={example.id}>
                  <button
                    type="button"
                    onClick={() => onSubmit(example.situation)}
                    title={example.situation}
                    className="min-h-[44px] rounded-control border border-line px-3 py-2 text-left transition-colors hover:border-indigo hover:bg-paper-deep"
                  >
                    <span className="flex flex-col">
                      <span lang="kn" className="kn text-body leading-[1.5] text-ink">
                        {t(`example.${example.labelKey}`)}
                      </span>
                      <span lang="en" className="text-[13px] leading-tight text-ink-soft">
                        {sub(`example.${example.labelKey}`)}
                      </span>
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <GaadePoster className="lg:sticky lg:top-8" />
      </div>
    </main>
  );
}
