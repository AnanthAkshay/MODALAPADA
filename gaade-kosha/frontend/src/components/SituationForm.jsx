import React from 'react';
import { Mic, MicOff, Globe } from 'lucide-react';
import { btnPrimary } from '../lib/ui';
import { useCopy } from '../i18n';

const segmentBase =
  'inline-flex min-h-[40px] items-center rounded-[9px] px-3 text-meta font-medium transition-colors';

export default function SituationForm({ value, onChange, onSubmit, speech, inputRef, onSelectLocale }) {
  const { t, sub, locale, other } = useCopy();
  const {
    supported,
    listening,
    lang,
    setLang,
    interim,
    error,
    dismissError,
    toggle,
    timerSeconds,
    isTranscribing,
    notice,
  } = speech;

  const handleLanguageChange = (newLocale) => {
    if (onSelectLocale) {
      onSelectLocale(newLocale);
    }
    if (setLang) {
      setLang(newLocale === 'kn' ? 'kn-IN' : 'en-IN');
    }
  };

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
          <span lang={locale} className={`${locale === 'kn' ? 'kn' : ''} leading-tight`}>
            {t('home.find')}
          </span>
          <span lang={other} className={`${other === 'kn' ? 'kn' : ''} text-[0.8em] leading-tight`}>
            {sub('home.find')}
          </span>
        </button>
      </div>

      {/* Whole-site language switch replacing separate 'Speak in' toggle */}
      <div className="mt-4 flex flex-wrap items-center gap-x-3 gap-y-2">
        <label className="flex items-center gap-1.5 text-meta text-ink">
          <Globe size={16} strokeWidth={1.75} aria-hidden="true" className="text-ink-soft" />
          <span className="font-medium">
            <span lang="kn" className="kn">ಭಾಷೆ</span>
            <span className="mx-1 text-ink-soft">/</span>
            <span lang="en">Language</span>:
          </span>
        </label>

        <div
          role="group"
          aria-label={t('common.languageSelect')}
          className="inline-flex rounded-control border border-line bg-paper-deep p-1"
        >
          <button
            type="button"
            onClick={() => handleLanguageChange('kn')}
            aria-pressed={locale === 'kn'}
            className={`${segmentBase} ${
              locale === 'kn' ? 'bg-turmeric-wash text-ink font-semibold' : 'text-ink-soft hover:text-ink'
            }`}
          >
            <span lang="kn" className="kn leading-tight">
              ಕನ್ನಡ
            </span>
          </button>
          <button
            type="button"
            onClick={() => handleLanguageChange('en')}
            aria-pressed={locale === 'en'}
            className={`${segmentBase} ${
              locale === 'en' ? 'bg-turmeric-wash text-ink font-semibold' : 'text-ink-soft hover:text-ink'
            }`}
          >
            <span lang="en" className="leading-tight">
              English
            </span>
          </button>
        </div>
      </div>

      {!supported && (
        <p className="mt-3 text-meta leading-[1.6] text-ink-soft">
          <span lang={locale} className={`${locale === 'kn' ? 'kn' : ''} block leading-[1.7]`}>
            {t('home.voiceUnsupported')}
          </span>
          <span lang={other} className={`${other === 'kn' ? 'kn' : ''} block text-[0.8em]`}>
            {sub('home.voiceUnsupported')}
          </span>
        </p>
      )}

      {listening || isTranscribing ? (
        <div className="mt-4 rounded-control border border-line bg-paper-deep px-4 py-3">
          <div className="flex items-center justify-between">
            <p className="flex items-center gap-2 text-meta font-medium text-kumkum">
              <span
                aria-hidden="true"
                className="h-2 w-2 shrink-0 rounded-full bg-kumkum animate-mic-dot motion-reduce:animate-none"
              />
              <span lang={locale} className={`${locale === 'kn' ? 'kn' : ''} leading-[1.7]`}>
                {isTranscribing
                  ? (locale === 'kn' ? 'ಧ್ವನಿಯನ್ನು ಪರಿವರ್ತಿಸಲಾಗುತ್ತಿದೆ...' : 'Transcribing audio...')
                  : t('home.listening')}
              </span>
            </p>
            {timerSeconds > 0 ? (
              <span className="font-mono text-[12px] text-kumkum bg-kumkum/10 px-2 py-0.5 rounded">
                00:{String(timerSeconds).padStart(2, '0')} / 00:30
              </span>
            ) : null}
          </div>
          <p lang={other} className={`${other === 'kn' ? 'kn' : ''} text-[0.8em] text-ink-soft`}>
            {isTranscribing
              ? (other === 'kn' ? 'ಧ್ವನಿಯನ್ನು ಪರಿವರ್ತಿಸಲಾಗುತ್ತಿದೆ...' : 'Transcribing audio...')
              : sub('home.listening')}
          </p>
          {notice ? (
            <p className="mt-1 text-[12px] font-medium text-turmeric">{notice}</p>
          ) : null}
          <p
            lang={lang === 'kn-IN' ? 'kn' : 'en'}
            className={`mt-1 min-h-[1.7em] break-words text-body leading-[1.7] text-ink ${
              lang === 'kn-IN' ? 'kn' : ''
            }`}
          >
            {interim || t('home.speakNow')}
          </p>
          <p className="mt-1 text-meta leading-[1.6] text-ink-soft">
            <span lang={locale} className={`${locale === 'kn' ? 'kn' : ''} block leading-[1.7]`}>
              {t('home.transcriptHint')}
            </span>
            <span lang={other} className={`${other === 'kn' ? 'kn' : ''} block text-[0.8em]`}>
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
            <span lang={locale} className={`${locale === 'kn' ? 'kn' : ''} block leading-[1.7]`}>
              {t(`speech.${error}`)}
            </span>
            <span lang={other} className={`${other === 'kn' ? 'kn' : ''} block text-[0.8em] text-ink-soft`}>
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
