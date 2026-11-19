import React, { useCallback, useEffect, useRef, useState } from 'react';
import TopBar from './components/TopBar';
import HomeScreen from './components/HomeScreen';
import ResultScreen from './components/ResultScreen';
import BrowseScreen from './components/BrowseScreen';
import SiteFooter from './components/SiteFooter';
import ConsentModal from './components/ConsentModal';
import useSpeechRecognition from './hooks/useSpeechRecognition';
import { fetchHealth, matchSituation } from './lib/api';
import { applyTheme, readTheme, watchSystemTheme } from './lib/theme';
import { LocaleProvider, readLocale, useCopy, writeLocale } from './i18n';

function SkipLink() {
  const { t } = useCopy();
  return (
    <a
      href="#main"
      className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-control focus:border focus:border-line focus:bg-paper focus:px-4 focus:py-2 focus:text-body"
    >
      {t('nav.skip')}
    </a>
  );
}

export default function App() {
  const [view, setView] = useState('home');
  const [inputText, setInputText] = useState('');
  const [match, setMatch] = useState(null);
  const [lastQuery, setLastQuery] = useState('');
  const [matchOrigin, setMatchOrigin] = useState('input');
  const [altIndex, setAltIndex] = useState(0);
  const [health, setHealth] = useState({ status: 'checking', gaades: 226 });
  const [theme, setTheme] = useState(() => readTheme());
  const [locale, setLocale] = useState(() => readLocale());
  const [consentOpen, setConsentOpen] = useState(false);
  const busy = useRef(false);

  const showDebug = typeof window !== 'undefined' && window.location.search.includes('debug=1');

  useEffect(() => {
    applyTheme(theme);
  }, [theme]);

  useEffect(() => watchSystemTheme(setTheme), []);

  useEffect(() => {
    writeLocale(locale);
    document.documentElement.lang = locale;
  }, [locale]);

  useEffect(() => {
    const controller = new AbortController();
    fetchHealth(controller.signal)
      .then((data) =>
        setHealth({ status: data.status === 'healthy' ? 'ok' : 'degraded', gaades: data.gaades_count }),
      )
      .catch((error) => {
        if (controller.signal.aborted || (error && error.name === 'AbortError')) return;
        setHealth({ status: 'offline', gaades: 226 });
      });
    return () => controller.abort();
  }, []);

  // Voice transcripts append or replace situation text, keeping it editable before sending
  const handleTranscript = useCallback((chunk) => {
    setInputText((previous) => {
      if (!previous.trim()) return chunk;
      return previous.endsWith(' ') ? `${previous}${chunk}` : `${previous} ${chunk}`;
    });
  }, []);

  const speech = useSpeechRecognition({ onTranscript: handleTranscript });
  const stopListening = speech.stop;

  const runMatch = useCallback(
    async (rawText) => {
      const text = (rawText ?? inputText).trim();
      if (!text || busy.current) return;

      busy.current = true;
      stopListening();
      setInputText(text);
      setLastQuery(text);
      setAltIndex(0);
      setMatchOrigin('input');
      setMatch({ phase: 'loading' });
      setView('result');
      window.scrollTo({ top: 0 });

      try {
        const data = await matchSituation(text);
        setMatch({ phase: 'ready', data });
      } catch (error) {
        setMatch({
          phase: 'error',
          kind: error?.kind === 'network' ? 'network' : 'http',
          status: error?.status,
        });
        if (error?.kind === 'network') setHealth({ status: 'offline', gaades: 226 });
      } finally {
        busy.current = false;
      }
    },
    [inputText, stopListening],
  );

  const startNewSituation = useCallback(() => {
    setView('home');
    setMatch(null);
    setAltIndex(0);
    setInputText('');
  }, []);

  const openGaade = useCallback((item) => {
    setMatch({
      phase: 'ready',
      data: {
        status: 'browse',
        message: '',
        best: { ...item, explanation: null, confidence: null },
        alternatives: [],
      },
    });
    setAltIndex(0);
    setMatchOrigin('browse');
    setView('result');
    window.scrollTo({ top: 0 });
  }, []);

  return (
    <LocaleProvider locale={locale}>
      <div className="flex min-h-dvh flex-col bg-paper">
        <SkipLink />

        <TopBar
          view={view}
          onNavigate={setView}
          theme={theme}
          onToggleTheme={() => setTheme((current) => (current === 'dark' ? 'light' : 'dark'))}
          locale={locale}
          onToggleLocale={() => setLocale((current) => (current === 'kn' ? 'en' : 'kn'))}
          status={health.status === 'offline'}
          onOpenConsent={() => setConsentOpen(true)}
        />

        <div className="flex-1">
          {view === 'home' ? (
            <HomeScreen
              inputValue={inputText}
              onInputChange={setInputText}
              onSubmit={runMatch}
              speech={speech}
            />
          ) : null}

          {view === 'result' ? (
            <ResultScreen
              match={match}
              query={lastQuery}
              altIndex={altIndex}
              fromBrowse={matchOrigin === 'browse'}
              onPromote={() => setAltIndex((current) => current + 1)}
              onSelect={setAltIndex}
              onNewSituation={startNewSituation}
              onRetry={() => runMatch(lastQuery)}
              onBackToBrowse={() => setView('browse')}
            />
          ) : null}

          {view === 'browse' ? <BrowseScreen onOpen={openGaade} /> : null}
        </div>

        <SiteFooter gaadeCount={health.gaades} onOpenConsent={() => setConsentOpen(true)} />

        <ConsentModal isOpen={consentOpen} onClose={() => setConsentOpen(false)} />

        {/* Debug Line (?debug=1) */}
        {showDebug && match?.data && (
          <aside
            role="status"
            aria-label="Matcher Debug Info"
            className="fixed bottom-0 left-0 right-0 z-40 flex flex-wrap items-center gap-4 border-t border-turmeric bg-paper-deep/95 px-4 py-2 font-mono text-[12px] text-ink shadow-lg backdrop-blur-sm"
          >
            <span className="rounded bg-turmeric/20 px-2 py-0.5 font-bold text-turmeric">DEBUG (?debug=1)</span>
            <span>Backend: <strong>{match.data.matcher_backend || 'tfidf'}</strong></span>
            <span>Status: <strong>{match.data.status}</strong></span>
            {match.data.best?.confidence !== undefined && (
              <span>Confidence: <strong>{Math.round(match.data.best.confidence * 100)}%</strong></span>
            )}
            <span>ID: <strong>{match.data.best?.gaade_id || 'none'}</strong></span>
          </aside>
        )}
      </div>
    </LocaleProvider>
  );
}
