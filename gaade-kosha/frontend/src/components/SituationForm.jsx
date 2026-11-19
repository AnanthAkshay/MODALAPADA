import React from 'react';
import { Mic, MicOff } from 'lucide-react';
import { btnPrimary } from '../lib/ui';
import { useCopy } from '../i18n';

const segmentBase =
  'inline-flex min-h-[40px] items-center rounded-[9px] px-3 text-meta font-medium transition-colors';

export default function SituationForm({ value, onChange, onSubmit, speech, inputRef }) {
  const { t, sub, locale, other } = useCopy();
  const { supported, listening, lang, setLang, interim, error, dismissError, toggle } = speech;

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        onSubmit(value);
      }}
      className="mt-8"
    >
      <div className="flex flex-wrap items-center gap-3">
        {supported ? (
          <button
            type="button"
            onClick={toggle}
            aria-pressed={listening}
            aria-label={listening ? t('home.micStop') : t('home.micStart')}
            className="relative order-2 flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-kumkum text-on-kumkum transition-colors hover:bg-kumkum-hover focus-visible:outline-offset-4 sm:order-1"
          >
            {listening ? (
              <MicOff size={22} strokeWidth={1.75} aria-hidden="true" />
            ) : (
              <Mic size={22} strokeWidth={1.75} aria-hidden="true" />
            )}
            {listening ? (
              <span
                aria-hidden="true"
                className="pointer-events-none absolute inset-0 rounded-full border-2 border-kumkum animate-mic-ring motion-reduce:animate-none"
              />
            ) : null}
          </button>
        ) : null}

        <label className="order-1 basis-full sm:order-2 sm:basis-0 sm:flex-1">
          <span className="sr-only">{t('home.inputLabel')}</span>
          <input
            ref={inputRef}
            type="text"
            value={value}
            onChange={(event) => onChange(event.target.value)}
            placeholder={t('home.placeholder')}
            autoComplete="off"
            className={`h-14 w-full min-w-0 rounded-control border border-line bg-paper-deep px-4 text-body text-ink placeholder:text-ink-soft focus-visible:outline-offset-0 ${
              locale === 'kn' ? 'kn' : ''
            }`}
          />
        </label>

        <button
          type="submit"
          disabled={!value.trim()}
          className={`${btnPrimary} order-3 ml-auto h-14 flex-col gap-0 px-5 sm:ml-0`}
        >
          <span lang="kn" className="kn leading-tight">
            {t('home.find')}
          </span>
          {/* Inherits the button's colour so it follows the disabled state too:
              text-on-kumkum would stay near-paper and vanish on paper-deep. */}
          <span lang={other} className="text-[0.8em] leading-tight">
            {sub('home.find')}
          </span>
        </button>
      </div>

      {supported ? (
        <div className="mt-4 flex flex-wrap items-center gap-x-3 gap-y-2">
          <span className="flex flex-col text-meta text-ink">
            <span lang="kn" className="kn leading-[1.7]">
              {t('home.speak')}:
            </span>
            <span lang={other} className="text-[0.8em] leading-tight text-ink-soft">
              {sub('home.speak')}:
            </span>
          </span>

          <div
            role="group"
            aria-label="Speech recognition language"
            className="inline-flex rounded-control border border-line bg-paper-deep p-1"
          >
            <button
              type="button"
              onClick={() => setLang('kn-IN')}
              aria-pressed={lang === 'kn-IN'}
              className={`${segmentBase} ${
                lang === 'kn-IN' ? 'bg-turmeric-wash text-ink' : 'text-ink-soft hover:text-ink'
              }`}
            >
              <span lang="kn" className="kn leading-tight">
                ಕನ್ನಡ
              </span>
            </button>
            <button
              type="button"
              onClick={() => setLang('en-IN')}
              aria-pressed={lang === 'en-IN'}
              className={`${segmentBase} ${
                lang === 'en-IN' ? 'bg-turmeric-wash text-ink' : 'text-ink-soft hover:text-ink'
              }`}
            >
              English
            </button>
          </div>
        </div>
      ) : (
        <p className="mt-4 text-meta leading-[1.6] text-ink-soft">
          <span lang="kn" className="kn block leading-[1.7]">
            {t('home.voiceUnsupported')}
          </span>
          <span lang={other} className="block text-[0.8em]">
            {sub('home.voiceUnsupported')}
          </span>
        </p>
      )}

      {listening ? (
        <div className="mt-4 rounded-control border border-line bg-paper-deep px-4 py-3">
          <p className="flex items-center gap-2 text-meta font-medium text-kumkum">
            <span
              aria-hidden="true"
              className="h-2 w-2 shrink-0 rounded-full bg-kumkum animate-mic-dot motion-reduce:animate-none"
            />
            <span lang="kn" className="kn leading-[1.7]">
              {t('home.listening')}
            </span>
          </p>
          <p lang={other} className="text-[0.8em] text-ink-soft">
            {sub('home.listening')}
          </p>
          <p
            lang={lang === 'kn-IN' ? 'kn' : 'en'}
            className={`mt-1 min-h-[1.7em] break-words text-body leading-[1.7] text-ink ${
              lang === 'kn-IN' ? 'kn' : ''
            }`}
          >
            {interim || t('home.speakNow')}
          </p>
          <p className="mt-1 text-meta leading-[1.6] text-ink-soft">
            <span lang="kn" className="kn block leading-[1.7]">
              {t('home.transcriptHint')}
            </span>
            <span lang={other} className="block text-[0.8em]">
              {sub('home.transcriptHint')}
            </span>
          </p>
        </div>
      ) : null}

      <p className="sr-only" role="status" aria-live="polite">
        {listening ? `${t('home.listening')} ${interim}` : ''}
      </p>

      {error ? (
        <div
          role="alert"
          className="mt-3 flex flex-wrap items-start gap-x-3 gap-y-1 border-l-2 border-kumkum pl-3 text-meta text-ink"
        >
          <span className="max-w-[52ch]">
            <span lang="kn" className="kn block leading-[1.7]">
              {t(`speech.${error}`)}
            </span>
            <span lang={other} className="block text-[0.8em] text-ink-soft">
              {sub(`speech.${error}`)}
            </span>
          </span>
          <button
            type="button"
            onClick={dismissError}
            className="min-h-[44px] text-ink-soft underline underline-offset-4 hover:text-ink"
          >
            {t('home.dismiss')}
          </button>
        </div>
      ) : null}
    </form>
  );
}
