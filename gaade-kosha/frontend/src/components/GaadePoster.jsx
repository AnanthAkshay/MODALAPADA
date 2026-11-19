import React, { useEffect, useState } from 'react';
import { fetchGaades } from '../lib/api';
import { useCopy } from '../i18n';
import AudioPlayer from './AudioPlayer';

/**
 * Gaades run from four to fifty-six characters. Stepping the size down with
 * length keeps every gaade inside the same three-line block, so the card height
 * and the play button stay put no matter which one lands here.
 */
function posterSize(text = '') {
  if (text.length <= 24) return 'text-poster-hero';
  if (text.length <= 36) return 'text-poster-lg';
  if (text.length <= 48) return 'text-poster-md';
  return 'text-poster-sm';
}

/**
 * "Gaade of the moment": one real gaade from /api/gaades, picked at random on
 * each load. Falls back to a fixed sample if the collection is slow or down.
 */
export default function GaadePoster({ className = '' }) {
  const { t } = useCopy();
  const [state, setState] = useState({ phase: 'loading', item: null });

  useEffect(() => {
    const controller = new AbortController();
    const fallbackTimer = window.setTimeout(() => {
      setState((current) => (current.item ? current : { phase: 'fallback', item: null }));
    }, 4000);

    (async () => {
      try {
        const first = await fetchGaades({ limit: 1 }, controller.signal);
        const total = Math.max(1, first.total || 1);
        const offset = Math.floor(Math.random() * total);
        const page = await fetchGaades({ limit: 1, offset }, controller.signal);
        const item = page.items?.[0] || first.items?.[0] || null;
        window.clearTimeout(fallbackTimer);
        setState(item ? { phase: 'ready', item } : { phase: 'fallback', item: null });
      } catch (error) {
        if (error && error.name === 'AbortError') return;
        window.clearTimeout(fallbackTimer);
        setState({ phase: 'fallback', item: null });
      }
    })();

    return () => {
      controller.abort();
      window.clearTimeout(fallbackTimer);
    };
  }, []);

  const fallback = {
    gaade: t('poster.fallbackGaade'),
    english: t('poster.fallbackEnglish'),
    audio_url: null,
    gaade_id: '',
  };
  const item = state.item || fallback;

  return (
    <aside className={`hidden lg:block ${className}`}>
      <div className="rounded-surface border border-indigo bg-paper px-6 py-7">
        <p className="text-meta text-ink-soft">{t('poster.label')}</p>

        <span aria-hidden="true" className="mx-auto mt-4 block h-[2px] w-12 bg-turmeric" />

        {state.phase === 'loading' ? (
          <div aria-busy="true" className="mt-6 animate-pulse motion-reduce:animate-none">
            <div className="mx-auto h-6 w-11/12 rounded bg-paper-deep" />
            <div className="mx-auto mt-3 h-6 w-8/12 rounded bg-paper-deep" />
            <div className="mx-auto mt-5 h-3 w-6/12 rounded bg-paper-deep" />
          </div>
        ) : (
          <>
            {/* Three lines at the largest size: the block never resizes. */}
            <div className="mt-5 flex min-h-[204px] items-center justify-center">
              <p
                lang="kn"
                className={`kn-serif break-words text-center ${posterSize(item.gaade)} font-bold text-indigo`}
              >
                {item.gaade}
              </p>
            </div>
            {/* Two lines at the meta size, so a long translation cannot push the player. */}
            <div className="mt-3 flex min-h-[48px] items-start justify-center">
              <p lang="en" className="break-words text-center text-meta italic leading-[1.7] text-ink-soft">
                {item.english}
              </p>
            </div>
          </>
        )}

        <div className="mt-6 flex items-center justify-center gap-3">
          <AudioPlayer
            audioUrl={item.audio_url}
            gaadeId={item.gaade_id}
            variant="quiet"
            withWaveform
          />
        </div>
      </div>
    </aside>
  );
}
