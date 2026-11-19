import React, { useRef } from 'react';
import SituationForm from './SituationForm';
import GaadePoster from './GaadePoster';
import { EXAMPLES } from '../data/examples';
import { useCopy } from '../i18n';

export default function HomeScreen({ inputValue, onInputChange, onSubmit, speech, onSelectLocale }) {
  const { t, sub, locale, other } = useCopy();
  const inputRef = useRef(null);

  return (
    <main id="main" className="mx-auto w-full max-w-content px-4 pb-16 pt-10 sm:px-8 sm:pt-16">
      <div className="grid items-start gap-12 lg:grid-cols-[minmax(0,1fr)_384px] lg:gap-14">
        <div className="min-w-0">
          <h1
            lang={locale}
            className={`break-words text-headline font-bold leading-[1.3] text-indigo wrap-balance ${
              locale === 'kn' ? 'kn-serif' : 'font-serif'
            }`}
          >
            {t('home.headline')}
          </h1>

          <p
            lang={locale}
            className={`mt-4 max-w-[32ch] break-words text-body-lg leading-[1.6] text-ink ${
              locale === 'kn' ? 'kn' : ''
            }`}
          >
            {t('home.subline')}
          </p>
          <p
            lang={other}
            className={`mt-1 max-w-[44ch] text-meta leading-[1.6] text-ink-soft ${
              other === 'kn' ? 'kn' : ''
            }`}
          >
            {sub('home.subline')}
          </p>

          <SituationForm
            inputRef={inputRef}
            value={inputValue}
            onChange={onInputChange}
            onSubmit={onSubmit}
            speech={speech}
            onSelectLocale={onSelectLocale}
          />

          <div className="mt-10">
            <p
              lang={locale}
              className={`text-meta leading-[1.7] text-ink ${locale === 'kn' ? 'kn' : ''}`}
            >
              {t('home.examples')}
            </p>
            <p
              lang={other}
              className={`text-[13px] leading-tight text-ink-soft ${other === 'kn' ? 'kn' : ''}`}
            >
              {sub('home.examples')}
            </p>

            <ul className="mt-3 flex flex-wrap gap-2">
              {EXAMPLES.map((example) => {
                const payload =
                  locale === 'kn' && example.situation_kn
                    ? example.situation_kn
                    : example.situation;

                return (
                  <li key={example.id}>
                    <button
                      type="button"
                      onClick={() => onSubmit(payload)}
                      title={payload}
                      className="min-h-[44px] rounded-control border border-line px-3 py-2 text-left transition-colors hover:border-indigo hover:bg-paper-deep"
                    >
                      <span className="flex flex-col">
                        <span
                          lang={locale}
                          className={`text-body leading-[1.5] text-ink ${
                            locale === 'kn' ? 'kn' : ''
                          }`}
                        >
                          {t(`example.${example.labelKey}`)}
                        </span>
                        <span
                          lang={other}
                          className={`text-[13px] leading-tight text-ink-soft ${
                            other === 'kn' ? 'kn' : ''
                          }`}
                        >
                          {sub(`example.${example.labelKey}`)}
                        </span>
                      </span>
                    </button>
                  </li>
                );
              })}
            </ul>
          </div>
        </div>

        <GaadePoster className="mt-8 lg:mt-0 lg:sticky lg:top-8" />
      </div>
    </main>
  );
}
