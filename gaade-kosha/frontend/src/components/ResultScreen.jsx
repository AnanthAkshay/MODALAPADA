import React from 'react';
import { ArrowLeft, RefreshCw } from 'lucide-react';
import AudioPlayer from './AudioPlayer';
import ExplanationTTS from './ExplanationTTS';
import Alternatives from './Alternatives';
import ManuscriptStrip from './ManuscriptStrip';
import KasutiBorder from './KasutiBorder';
import ResultSkeleton from './ResultSkeleton';
import { btnPrimary, btnText } from '../lib/ui';
import { useCopy } from '../i18n';

export default function ResultScreen({
  match,
  query,
  altIndex = 0,
  onPromote,
  onSelect,
  onNewSituation,
  onRetry,
  fromBrowse = false,
  onBackToBrowse,
}) {
  const { t } = useCopy();
  if (!match) return null;

  return (
    <main id="main" className="mx-auto w-full max-w-read px-4 pb-20 pt-8 sm:px-8 sm:pt-12">
      {fromBrowse && onBackToBrowse ? (
        <button type="button" onClick={onBackToBrowse} className={`${btnText} mb-6`}>
          <ArrowLeft size={16} strokeWidth={1.75} aria-hidden="true" />
          <span lang="kn" className="kn leading-[1.7]">
            {t('result.backToBrowse')}
          </span>
        </button>
      ) : null}

      {match.phase === 'loading' ? <ResultSkeleton /> : null}

      {match.phase === 'error' ? (
        <ErrorBlock match={match} query={query} onRetry={onRetry} onNewSituation={onNewSituation} />
      ) : null}

      {match.phase === 'ready' ? (
        <ReadyView
          data={match.data}
          query={query}
          altIndex={altIndex}
          onPromote={onPromote}
          onSelect={onSelect}
          onNewSituation={onNewSituation}
          fromBrowse={fromBrowse}
          onBackToBrowse={onBackToBrowse}
        />
      ) : null}
    </main>
  );
}

function SectionTitle({ k }) {
  const { t, sub, other } = useCopy();
  return (
    <h3 className="flex flex-col">
      <span lang="kn" className="kn text-body font-semibold leading-[1.7] text-indigo">
        {t(k)}
      </span>
      <span lang={other} className="text-[13px] leading-tight text-ink-soft">
        {sub(k)}
      </span>
    </h3>
  );
}

function ActionLabel({ k, vars }) {
  const { t, sub, other } = useCopy();
  return (
    <span className="flex flex-col items-start">
      <span lang="kn" className="kn leading-[1.5]">
        {t(k, vars)}
      </span>
      <span lang={other} className="text-[0.8em] leading-tight opacity-80">
        {sub(k, vars)}
      </span>
    </span>
  );
}

function ReadyView({ data, query, altIndex, onPromote, onSelect, onNewSituation, fromBrowse, onBackToBrowse }) {
  const { t, sub, other, digits, themeName, themeSub, locale } = useCopy();
  const pool = data.best ? [data.best, ...(data.alternatives || [])] : [];
  const index = Math.min(altIndex, Math.max(pool.length - 1, 0));
  const item = pool[index] || null;

  if (!item) {
    return (
      <NoticeBlock
        status={data.status}
        message={data.message}
        onNewSituation={onNewSituation}
        onBackToBrowse={onBackToBrowse}
        fromBrowse={fromBrowse}
      />
    );
  }

  const hasMore = index < pool.length - 1;
  const isAmbiguous = data.status === 'ambiguous';
  const confidenceVal = typeof item.confidence === 'number' ? item.confidence : null;
  const isLowConfidence = !isAmbiguous && confidenceVal !== null && confidenceVal > 0 && confidenceVal < 0.60;
  const alternatives = pool.slice(1);
  const regionKnown = item.region && item.region !== 'UNVERIFIED' && item.region.trim() !== '';

  const queryHasKannada = Boolean(query && /[\u0C80-\u0CFF]/.test(query));
  const preferKannadaReason = locale === 'kn' || data.detected_lang === 'kn' || queryHasKannada;
  const reasonText = preferKannadaReason
    ? (item.reason_kn || item.explanation)
    : (item.reason_en || item.explanation);
  const reasonLang = preferKannadaReason && item.reason_kn ? 'kn' : 'en';

  return (
    <div className="animate-fade-in motion-reduce:animate-none">
      {isAmbiguous ? (
        <p className="mb-6 flex flex-col border-l-2 border-turmeric pl-4 text-meta">
          <span lang="kn" className="kn leading-[1.7] text-ink">
            {t('result.ambiguous')}
          </span>
          <span lang={other} className="text-[0.8em] text-ink-soft">
            {sub('result.ambiguous')}
          </span>
        </p>
      ) : isLowConfidence ? (
        <p className="mb-6 flex flex-col border-l-2 border-turmeric pl-4 text-meta">
          <span lang="kn" className="kn leading-[1.7] text-ink">
            {t('result.lowConfidence')}
          </span>
          <span lang={other} className="text-[0.8em] text-ink-soft">
            {sub('result.lowConfidence')}
          </span>
        </p>
      ) : null}

      {query && !fromBrowse ? (
        <div className="mb-4">
          <p className="flex flex-wrap items-baseline gap-x-2">
            <span lang="kn" className="kn text-meta leading-[1.7] text-ink-soft">
              {t('result.described')}
            </span>
            <span lang={other} className="text-[12px] leading-tight text-ink-soft">
              {sub('result.described')}
            </span>
          </p>
          <p className="truncate text-meta leading-[1.7] text-ink">“{query}”</p>
        </div>
      ) : null}

      <ManuscriptStrip item={item} />

      <div className="mt-8 flex flex-wrap items-start justify-center gap-x-4 gap-y-3">
        <AudioPlayer audioUrl={item.audio_url} gaadeId={item.gaade_id} />
        <ExplanationTTS text={reasonText || item.explanation || ''} />
      </div>

      <KasutiBorder className="mt-9" />

      <div className="mt-8 grid gap-8 sm:grid-cols-2 sm:gap-0">
        <section className="sm:border-r sm:border-line sm:pr-8">
          <SectionTitle k="result.meaning" />
          {/* The collection's `meaning` field is written in English. */}
          <p lang="en" className="mt-2 break-words text-body-lg leading-[1.75] text-ink">
            {item.meaning}
          </p>
        </section>

        <section className="sm:pl-8">
          <SectionTitle k="result.whyItFits" />
          {reasonText ? (
            <p
              lang={reasonLang}
              className={`mt-2 text-body-lg leading-[1.7] text-ink ${reasonLang === 'kn' ? 'kn leading-[1.8]' : ''}`}
            >
              {reasonText}
            </p>
          ) : (
            <p className="mt-2 flex flex-col text-body leading-[1.7] text-ink-soft">
              <span lang="kn" className="kn leading-[1.7]">
                {t(fromBrowse ? 'result.explanationFromBrowse' : 'result.explanationForFirst')}
              </span>
              <span lang={other} className="mt-1 text-[0.8em] leading-[1.6]">
                {sub(fromBrowse ? 'result.explanationFromBrowse' : 'result.explanationForFirst')}
              </span>
            </p>
          )}
        </section>
      </div>

      <div className="mt-10 flex flex-wrap gap-x-8 gap-y-3 border-t border-line pt-5">
        <span className="flex flex-col">
          <span lang="kn" className="kn text-meta leading-[1.7] text-ink-soft">
            {t('result.theme')}: {item.theme ? themeName(item.theme) : t('result.themeUnverified')}
          </span>
          <span lang={other} className="text-[12px] leading-tight text-ink-soft">
            {sub('result.theme')}: {item.theme ? themeSub(item.theme) : sub('result.themeUnverified')}
          </span>
        </span>

        <span className="flex flex-col">
          <span lang="kn" className="kn text-meta leading-[1.7] text-ink-soft">
            {regionKnown ? `${t('result.region')}: ${item.region}` : t('result.regionUnverified')}
          </span>
          <span lang={other} className="text-[12px] leading-tight text-ink-soft">
            {regionKnown ? `${sub('result.region')}: ${item.region}` : sub('result.regionUnverified')}
          </span>
        </span>

        {confidenceVal !== null && confidenceVal > 0 ? (
          <span className="flex flex-col">
            <span lang="kn" className="kn text-meta leading-[1.7] text-ink-soft">
              ವಿಶ್ವಾಸಾರ್ಹತೆ: {digits(Math.round(confidenceVal * 100))}%
            </span>
            <span lang={other} className="text-[12px] leading-tight text-ink-soft">
              confidence: {Math.round(confidenceVal * 100)}%
            </span>
          </span>
        ) : null}

        <span className="flex flex-col">
          <span lang="kn" className="kn text-meta leading-[1.7] text-ink-soft">
            {digits(item.gaade_id)}
          </span>
          {index > 0 ? (
            <span lang="kn" className="kn text-[12px] leading-tight text-ink-soft">
              {t('result.alternative', { index: digits(index + 1), total: digits(pool.length) })}
            </span>
          ) : null}
        </span>

        <span className="flex flex-col">
          <span lang="kn" className="kn text-meta leading-[1.7] text-ink-soft">
            ಸ್ಥಿತಿ: {item.provenance || 'ಅಧಿಕೃತ (Canonical)'}
          </span>
          <span lang={other} className="text-[12px] leading-tight text-ink-soft">
            Status: {item.status === 'synthetic' ? 'Archival addition' : 'Verified canonical'}
          </span>
        </span>
      </div>

      <div className="mt-5 flex flex-wrap items-center gap-x-8 gap-y-2">
        <button type="button" onClick={onPromote} disabled={!hasMore} className={btnText}>
          <ActionLabel k="result.showAnother" />
        </button>
        <button type="button" onClick={onNewSituation} className={btnText}>
          <ActionLabel k="result.newSituation" />
        </button>
      </div>

      {isAmbiguous && alternatives.length ? (
        <Alternatives
          items={alternatives}
          activeIndex={index - 1}
          onChoose={(choice) => onSelect && onSelect(choice + 1)}
          titleKey="result.othersFit"
        />
      ) : null}
    </div>
  );
}

function NoticeBlock({ status, message, onNewSituation, onBackToBrowse, fromBrowse }) {
  const { t, sub, other } = useCopy();
  const titleKey = `result.notice.${status}`;
  const known = ['no_good_match', 'invalid_input', 'inappropriate_input', 'greeting', 'error'].includes(status);
  const resolved = known ? titleKey : 'result.notice.fallback';

  return (
    <section className="animate-fade-in border-l-2 border-turmeric pl-5 motion-reduce:animate-none">
      <h2 className="flex flex-col">
        <span lang="kn" className="kn-serif text-title font-bold leading-[1.7] text-indigo">
          {t(resolved)}
        </span>
        <span lang={other} className="text-meta leading-tight text-ink-soft">
          {sub(resolved)}
        </span>
      </h2>

      <p lang="en" className="mt-3 max-w-[54ch] text-body leading-[1.7] text-ink">
        {message}
      </p>

      {status === 'no_good_match' ? (
        <p className="mt-3 flex max-w-[54ch] flex-col">
          <span lang="kn" className="kn text-body leading-[1.7] text-ink">
            {t('result.noMatchTip')}
          </span>
          <span lang={other} className="mt-1 text-meta leading-[1.6] text-ink-soft">
            {sub('result.noMatchTip')}
          </span>
        </p>
      ) : null}

      <div className="mt-6 flex flex-wrap items-center gap-x-6 gap-y-2">
        <button type="button" onClick={onNewSituation} className={btnText}>
          <ActionLabel k="result.describeAnother" />
        </button>
        {fromBrowse && onBackToBrowse ? (
          <button type="button" onClick={onBackToBrowse} className={btnText}>
            <ActionLabel k="result.backToBrowse" />
          </button>
        ) : null}
      </div>
    </section>
  );
}

function ErrorBlock({ match, query, onRetry, onNewSituation }) {
  const { t, sub, other } = useCopy();
  const isNetwork = match.kind === 'network';
  const titleKey = isNetwork ? 'result.errorNetworkTitle' : 'result.errorHttpTitle';
  const bodyKey = isNetwork ? 'result.errorNetworkBody' : 'result.errorHttpBody';

  return (
    <section role="alert" className="animate-fade-in border-l-2 border-kumkum pl-5 motion-reduce:animate-none">
      <h2 className="flex flex-col">
        <span lang="kn" className="kn-serif text-title font-bold leading-[1.7] text-indigo">
          {t(titleKey)}
        </span>
        <span lang={other} className="text-meta leading-tight text-ink-soft">
          {sub(titleKey)}
        </span>
      </h2>

      <p className="mt-3 flex max-w-[54ch] flex-col">
        <span lang="kn" className="kn text-body leading-[1.7] text-ink-soft">
          {t(bodyKey, { status: match.status })}
        </span>
        <span lang={other} className="mt-1 text-meta leading-[1.6] text-ink-soft">
          {sub(bodyKey, { status: match.status })}
        </span>
      </p>

      {query ? (
        <p className="mt-3 truncate text-meta text-ink-soft">
          {t('result.queryLabel')}: “{query}”
        </p>
      ) : null}

      <div className="mt-6 flex flex-wrap items-center gap-4">
        <button type="button" onClick={onRetry} className={btnPrimary}>
          <RefreshCw size={16} strokeWidth={1.75} aria-hidden="true" />
          <span lang="kn" className="kn leading-[1.7]">
            {t('result.tryAgain')}
          </span>
        </button>
        <button type="button" onClick={onNewSituation} className={btnText}>
          <ActionLabel k="result.newSituation" />
        </button>
      </div>
    </section>
  );
}
