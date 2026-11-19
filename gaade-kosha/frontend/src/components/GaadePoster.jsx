import React, { useCallback, useEffect, useRef, useState } from 'react';
import { RefreshCw, AlertCircle } from 'lucide-react';
import { fetchRandomGaade } from '../lib/api';
import { useCopy } from '../i18n';
import AudioPlayer from './AudioPlayer';

const STORAGE_KEY = 'gaade_recent_random';

function getRecentExcludes() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (_) {
    return [];
  }
}

function recordRecentGaade(id) {
  if (!id) return;
  try {
    const existing = getRecentExcludes().filter((x) => x !== id);
    existing.unshift(id);
    if (existing.length > 5) existing.length = 5;
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(existing));
  } catch (_) {}
}

/**
 * Stepping the font size down with gaade length keeps the card height
 * stable and visually balanced across short and long proverbs.
 */
function posterSize(text = '') {
  if (text.length <= 24) return 'text-poster-hero';
  if (text.length <= 36) return 'text-poster-lg';
  if (text.length <= 48) return 'text-poster-md';
  return 'text-poster-sm';
}

/**
 * "Gaade of the moment": Canonical gaade with existing human audio.
 * Rotates on page refresh, avoids last 5 shown IDs, and supports instant "Show another".
 */
export default function GaadePoster({ className = '' }) {
  const { t, locale } = useCopy();
  const [state, setState] = useState({ phase: 'loading', item: null, error: null });
  const [isRotating, setIsRotating] = useState(false);
  const activeAbortRef = useRef(null);

  const loadRandom = useCallback(async (showSkeleton = true) => {
    if (activeAbortRef.current) {
      activeAbortRef.current.abort();
    }
    const controller = new AbortController();
    activeAbortRef.current = controller;

    if (showSkeleton) {
      setState((prev) => ({ ...prev, phase: 'loading', error: null }));
    }
    setIsRotating(true);

    try {
      const recent = getRecentExcludes().join(',');
      const item = await fetchRandomGaade(recent, controller.signal);
      recordRecentGaade(item.gaade_id);
      setState({ phase: 'ready', item, error: null });
    } catch (err) {
      if (err && err.name === 'AbortError') return;
      setState((prev) => ({
        phase: 'error',
        item: prev.item,
        error: err,
      }));
    } finally {
      setIsRotating(false);
    }
  }, []);

  useEffect(() => {
    loadRandom(true);
    return () => {
      if (activeAbortRef.current) {
        activeAbortRef.current.abort();
      }
    };
  }, [loadRandom]);

  const item = state.item;
  const meaningText = item
    ? locale === 'kn'
      ? item.meaning || item.english
      : item.english || item.meaning
    : '';

  return (
    <aside className={`w-full ${className}`}>
      <div className="rounded-surface border border-indigo bg-paper px-6 py-7 shadow-sm transition-colors">
        <div className="flex items-center justify-between">
          <p className="text-meta font-medium text-ink-soft">{t('poster.label')}</p>
          <button
            type="button"
            onClick={() => loadRandom(false)}
            disabled={isRotating}
            aria-label={t('poster.showAnother')}
            title={t('poster.showAnother')}
            className="inline-flex items-center gap-1.5 rounded-control px-2.5 py-1 text-meta text-ink-soft transition-colors hover:bg-paper-deep hover:text-indigo focus-visible:outline-offset-2"
          >
            <RefreshCw
              size={14}
              strokeWidth={2}
              className={`transition-transform duration-500 ${isRotating ? 'animate-spin' : ''}`}
              aria-hidden="true"
            />
            <span className="hidden sm:inline text-[13px]">{t('poster.showAnother')}</span>
          </button>
        </div>

        <span aria-hidden="true" className="mx-auto mt-3 block h-[2px] w-12 bg-turmeric" />

        {state.phase === 'loading' && !item ? (
          <div aria-busy="true" className="mt-6 animate-pulse motion-reduce:animate-none">
            <div className="mx-auto h-8 w-11/12 rounded bg-paper-deep" />
            <div className="mx-auto mt-3 h-8 w-8/12 rounded bg-paper-deep" />
            <div className="mx-auto mt-6 h-4 w-9/12 rounded bg-paper-deep" />
            <div className="mx-auto mt-2 h-4 w-7/12 rounded bg-paper-deep" />
            <div className="mx-auto mt-6 h-10 w-32 rounded-control bg-paper-deep" />
          </div>
        ) : state.phase === 'error' && !item ? (
          <div className="mt-6 py-6 text-center">
            <AlertCircle size={28} className="mx-auto text-kumkum" aria-hidden="true" />
            <p className="mt-3 text-meta text-ink">{t('poster.error')}</p>
            <button
              type="button"
              onClick={() => loadRandom(true)}
              className="mt-4 inline-flex items-center gap-2 rounded-control border border-line bg-paper-deep px-4 py-2 text-meta font-medium text-ink transition-colors hover:border-indigo hover:text-indigo"
            >
              <RefreshCw size={14} aria-hidden="true" />
              <span>{t('poster.retry')}</span>
            </button>
          </div>
        ) : item ? (
          <>
            <div className="mt-5 flex min-h-[170px] items-center justify-center">
              <p
                lang="kn"
                className={`kn-serif break-words text-center ${posterSize(item.gaade)} font-bold text-indigo leading-[1.6]`}
              >
                {item.gaade}
              </p>
            </div>

            <div className="mt-3 flex min-h-[52px] items-start justify-center">
              <p
                lang={locale}
                className={`break-words text-center text-meta italic leading-[1.7] text-ink-soft ${
                  locale === 'kn' ? 'kn' : ''
                }`}
              >
                {meaningText}
              </p>
            </div>

            <div className="mt-6 flex flex-col items-center justify-center gap-3">
              {item.audio_url && (
                <AudioPlayer
                  audioUrl={item.audio_url}
                  gaadeId={item.gaade_id}
                  variant="quiet"
                  withWaveform
                />
              )}

              <button
                type="button"
                onClick={() => loadRandom(false)}
                disabled={isRotating}
                className="mt-2 inline-flex sm:hidden items-center gap-1.5 rounded-control border border-line bg-paper-deep px-3 py-1.5 text-[13px] text-ink-soft hover:text-ink"
              >
                <RefreshCw size={13} className={isRotating ? 'animate-spin' : ''} aria-hidden="true" />
                <span>{t('poster.showAnother')}</span>
              </button>
            </div>
          </>
        ) : null}
      </div>
    </aside>
  );
}
