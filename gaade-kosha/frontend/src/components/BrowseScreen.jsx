import React, { useEffect, useRef, useState } from 'react';
import { Search } from 'lucide-react';
import AudioPlayer from './AudioPlayer';
import { fetchGaades, fetchThemes } from '../lib/api';
import { useCopy } from '../i18n';

export default function BrowseScreen({ onOpen }) {
  const { t, sub, locale, other, num, digits, themeName, themeSub } = useCopy();
  const [query, setQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const [theme, setTheme] = useState('');
  const [themes, setThemes] = useState([]);
  const [allThemesShown, setAllThemesShown] = useState(false);
  const [state, setState] = useState({ phase: 'loading', items: [], total: 0 });
  const requestId = useRef(0);

  useEffect(() => {
    const timer = window.setTimeout(() => setDebouncedQuery(query.trim()), 250);
    return () => window.clearTimeout(timer);
  }, [query]);

  useEffect(() => {
    const controller = new AbortController();
    fetchThemes(controller.signal)
      .then((data) => setThemes(data.items || []))
      .catch(() => setThemes([]));
    return () => controller.abort();
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    const current = (requestId.current += 1);
    setState((previous) => ({ ...previous, phase: 'loading' }));

    fetchGaades({ q: debouncedQuery, theme, limit: 300 }, controller.signal)
      .then((data) => {
        if (current !== requestId.current) return;
        setState({ phase: 'ready', items: data.items || [], total: data.total || 0 });
      })
      .catch((error) => {
        if (error && error.name === 'AbortError') return;
        if (current !== requestId.current) return;
        setState({ phase: 'error', items: [], total: 0 });
      });

    return () => controller.abort();
  }, [debouncedQuery, theme]);

  const chipClass = (active) =>
    `min-h-[44px] rounded-control border px-3 py-1.5 text-left transition-colors ${
      active
        ? 'border-indigo bg-turmeric-wash text-ink'
        : 'border-line text-ink hover:border-indigo hover:bg-paper-deep'
    }`;

  return (
    <main id="main" className="mx-auto w-full max-w-content px-4 pb-20 pt-8 sm:px-8 sm:pt-12">
      <div className="mx-auto max-w-read">
        <h1 className="flex flex-col">
          <span
            lang={locale}
            className={`${locale === 'kn' ? 'kn-serif' : 'font-serif'} break-words text-headline font-bold leading-[1.7] text-indigo`}
          >
            {t('browse.title')}
          </span>
          <span
            lang={other}
            className={`${other === 'kn' ? 'kn' : ''} text-body leading-tight text-ink-soft`}
          >
            {sub('browse.title')}
          </span>
        </h1>

        <p className="mt-4 flex flex-col">
          <span
            lang={locale}
            className={`${locale === 'kn' ? 'kn' : ''} text-body leading-[1.7] text-ink-soft`}
          >
            {state.phase === 'ready'
              ? t('browse.intro', { count: num(state.total) })
              : t('browse.introPending')}
          </span>
          <span
            lang={other}
            className={`${other === 'kn' ? 'kn' : ''} text-[0.8em] leading-[1.6] text-ink-soft`}
          >
            {state.phase === 'ready'
              ? sub('browse.intro', { count: num(state.total) })
              : sub('browse.introPending')}
          </span>
        </p>

        <div className="mt-6">
          <label className="relative block">
            <span className="sr-only">{t('browse.search')}</span>
            <Search
              size={18}
              strokeWidth={1.75}
              aria-hidden="true"
              className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-ink-soft"
            />
            <input
              type="search"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder={t('browse.search')}
              className="h-12 w-full rounded-control border border-line bg-paper-deep pl-11 pr-4 text-body text-ink placeholder:text-ink-soft focus-visible:outline-offset-0"
            />
          </label>
        </div>

        {themes.length ? (
          <div className="mt-3 flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => setTheme('')}
              aria-pressed={theme === ''}
              className={chipClass(theme === '')}
            >
              <span className="flex flex-col">
                <span
                  lang={locale}
                  className={`${locale === 'kn' ? 'kn' : ''} text-meta leading-[1.5]`}
                >
                  {t('browse.allThemes')}
                </span>
                <span
                  lang={other}
                  className={`${other === 'kn' ? 'kn' : ''} text-[11px] leading-tight text-ink-soft`}
                >
                  {sub('browse.allThemes')}
                </span>
              </span>
            </button>

            {(allThemesShown ? themes : themes.slice(0, 8)).map((entry) => (
              <button
                key={entry.theme}
                type="button"
                onClick={() => setTheme(entry.theme)}
                aria-pressed={theme === entry.theme}
                className={chipClass(theme === entry.theme)}
              >
                <span className="flex flex-col">
                  <span
                    lang={locale}
                    className={`${locale === 'kn' ? 'kn' : ''} text-meta leading-[1.5]`}
                  >
                    {themeName(entry.theme)} {num(entry.count)}
                  </span>
                  <span
                    lang={other}
                    className={`${other === 'kn' ? 'kn' : ''} text-[11px] leading-tight text-ink-soft`}
                  >
                    {themeSub(entry.theme)}
                  </span>
                </span>
              </button>
            ))}

            {themes.length > 8 ? (
              <button
                type="button"
                onClick={() => setAllThemesShown((shown) => !shown)}
                aria-expanded={allThemesShown}
                className="min-h-[44px] rounded-control px-1 text-left text-meta text-indigo underline underline-offset-4"
              >
                <span
                  lang={locale}
                  className={`${locale === 'kn' ? 'kn' : ''} leading-[1.7]`}
                >
                  {allThemesShown
                    ? t('browse.showFewerThemes')
                    : t('browse.showAllThemes', { count: num(themes.length) })}
                </span>
              </button>
            ) : null}
          </div>
        ) : null}
      </div>

      <div className="mx-auto mt-8 max-w-read">
        {state.phase === 'loading' ? (
          <div aria-busy="true" className="animate-pulse motion-reduce:animate-none">
            <p role="status" className="sr-only">
              {t('browse.loading')}
            </p>
            {[0, 1, 2, 3, 4].map((row) => (
              <div key={row} className="border-b border-line py-5">
                <div className="h-5 w-9/12 rounded bg-paper-deep" />
                <div className="mt-3 h-3 w-10/12 rounded bg-paper-deep" />
              </div>
            ))}
          </div>
        ) : null}

        {state.phase === 'error' ? (
          <p role="alert" className="border-l-2 border-kumkum pl-4 text-body text-ink">
            <span
              lang={locale}
              className={`${locale === 'kn' ? 'kn' : ''} block leading-[1.7]`}
            >
              {t('browse.loadError')}
            </span>
            <span
              lang={other}
              className={`${other === 'kn' ? 'kn' : ''} block text-[0.8em] text-ink-soft`}
            >
              {sub('browse.loadError')}
            </span>
          </p>
        ) : null}

        {state.phase === 'ready' && state.items.length === 0 ? (
          <div className="border-l-2 border-turmeric pl-4">
            <p className="text-body text-ink">
              <span
                lang={locale}
                className={`${locale === 'kn' ? 'kn' : ''} block leading-[1.7]`}
              >
                {t('browse.empty', { query: query.trim() })}
              </span>
              <span
                lang={other}
                className={`${other === 'kn' ? 'kn' : ''} block text-[0.8em] text-ink-soft`}
              >
                {sub('browse.empty', { query: query.trim() })}
              </span>
            </p>
            <button
              type="button"
              onClick={() => {
                setQuery('');
                setTheme('');
              }}
              className="mt-2 min-h-[44px] text-body text-indigo underline underline-offset-4"
            >
              {t('browse.clear')}
            </button>
          </div>
        ) : null}

        {state.phase === 'ready' && state.items.length ? (
          <ul className="border-t border-line">
            {state.items.map((item) => (
              <li key={item.gaade_id} className="border-b border-line">
                <div className="flex items-center gap-4 py-4">
                  <button
                    type="button"
                    onClick={() => onOpen(item)}
                    className="min-w-0 flex-1 rounded-control text-left"
                  >
                    <span lang="kn" className="kn-serif block break-words text-body-lg font-bold leading-[1.7] text-indigo">
                      {item.gaade}
                    </span>
                    <span className="mt-1 block truncate text-body leading-[1.7] text-ink-soft">
                      {item.meaning}
                    </span>
                    <span className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-meta text-ink-soft">
                      <span className="rounded-full border border-line px-2.5 py-0.5">
                        <span lang="kn" className="kn leading-[1.5]">
                          {themeName(item.theme)}
                        </span>
                      </span>
                      <span lang="kn" className="kn leading-[1.5]">
                        {digits(item.gaade_id)}
                      </span>
                    </span>
                  </button>
                  <AudioPlayer audioUrl={item.audio_url} gaadeId={item.gaade_id} variant="quiet" />
                </div>
              </li>
            ))}
          </ul>
        ) : null}
      </div>
    </main>
  );
}
