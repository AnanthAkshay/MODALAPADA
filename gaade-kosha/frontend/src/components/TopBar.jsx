import React from 'react';
import { Globe, Moon, Sun } from 'lucide-react';
import { useCopy } from '../i18n';
import KasutiBorder from './KasutiBorder';

export default function TopBar({
  view,
  onNavigate,
  theme,
  onToggleTheme,
  locale,
  onToggleLocale,
  status,
  onOpenConsent,
}) {
  const { t, sub, other } = useCopy();
  const isOffline = status === true || status === 'offline';

  return (
    <header>
      <div className="mx-auto flex min-h-[72px] max-w-content items-center gap-2 px-4 py-2 sm:px-8">
        <button
          type="button"
          onClick={() => onNavigate('home')}
          aria-current={view === 'home' ? 'page' : undefined}
          className="flex shrink-0 flex-col items-start rounded-control py-1"
        >
          <span
            lang={locale}
            className={`${locale === 'kn' ? 'kn' : ''} text-[24px] font-semibold leading-[1.15] text-ink sm:text-[28px]`}
          >
            {t('brand')}
          </span>
          <span
            lang={other}
            className={`${other === 'kn' ? 'kn' : ''} text-[12px] leading-tight text-ink-soft`}
          >
            {sub('brand')}
          </span>
        </button>

        <div className="ml-auto flex items-center gap-0 sm:gap-1">
          {/* Status Dot: Green when reachable, Red when offline */}
          {isOffline ? (
            <span
              className="mr-2 hidden items-center gap-1.5 text-meta text-kumkum md:inline-flex"
              title={t('nav.unreachable')}
            >
              <span aria-hidden="true" className="h-2 w-2 rounded-full bg-kumkum ring-2 ring-kumkum/30 animate-pulse" />
              <span lang={locale} className={`${locale === 'kn' ? 'kn' : ''} leading-[1.7]`}>
                {t('nav.unreachable')}
              </span>
            </span>
          ) : (
            <span
              className="mr-2 hidden items-center gap-1.5 text-meta text-emerald-600 dark:text-emerald-400 md:inline-flex"
              title={t('nav.connected')}
            >
              <span aria-hidden="true" className="h-2 w-2 rounded-full bg-emerald-500 ring-2 ring-emerald-500/30" />
              <span lang={locale} className={`${locale === 'kn' ? 'kn' : ''} leading-[1.7]`}>
                {t('nav.connected')}
              </span>
            </span>
          )}

          {/* Search / Home Nav */}
          <button
            type="button"
            onClick={() => onNavigate('home')}
            aria-current={view === 'home' ? 'page' : undefined}
            className={`inline-flex min-h-[44px] flex-col justify-center rounded-control px-2 text-left transition-colors hover:text-indigo sm:px-3 ${
              view === 'home' ? 'text-indigo font-semibold' : 'text-ink'
            }`}
          >
            <span
              lang={locale}
              className={`${locale === 'kn' ? 'kn' : ''} whitespace-nowrap text-[13px] leading-[1.5] sm:text-body`}
            >
              {t('nav.search')}
            </span>
            <span
              lang={other}
              className={`${other === 'kn' ? 'kn' : ''} hidden text-[11px] leading-tight text-ink-soft sm:block`}
            >
              {sub('nav.search')}
            </span>
          </button>

          <button
            type="button"
            onClick={() => onNavigate('browse')}
            aria-current={view === 'browse' ? 'page' : undefined}
            className={`inline-flex min-h-[44px] flex-col justify-center rounded-control px-2 text-left transition-colors hover:text-indigo sm:px-3 ${
              view === 'browse' ? 'text-indigo' : 'text-ink'
            }`}
          >
            <span
              lang={locale}
              className={`${locale === 'kn' ? 'kn' : ''} whitespace-nowrap text-[13px] leading-[1.5] sm:text-body`}
            >
              {t('nav.browse')}
            </span>
            <span
              lang={other}
              className={`${other === 'kn' ? 'kn' : ''} hidden text-[11px] leading-tight text-ink-soft sm:block`}
            >
              {sub('nav.browse')}
            </span>
          </button>

          {onOpenConsent && (
            <button
              type="button"
              onClick={onOpenConsent}
              className="inline-flex min-h-[44px] flex-col justify-center rounded-control px-2 text-left transition-colors hover:text-indigo sm:px-3 text-ink"
            >
              <span
                lang={locale}
                className={`${locale === 'kn' ? 'kn' : ''} whitespace-nowrap text-[13px] leading-[1.5] sm:text-body`}
              >
                {t('nav.consent')}
              </span>
              <span
                lang={other}
                className={`${other === 'kn' ? 'kn' : ''} hidden text-[11px] leading-tight text-ink-soft sm:block`}
              >
                {sub('nav.consent')}
              </span>
            </button>
          )}

          {/* Whole-site language switch in header */}
          <button
            type="button"
            onClick={onToggleLocale}
            aria-label={locale === 'kn' ? t('nav.switchToEnglish') : t('nav.switchToKannada')}
            className="inline-flex h-11 min-w-[44px] items-center justify-center rounded-control px-2 text-meta text-ink transition-colors hover:text-indigo"
          >
            <Globe size={18} strokeWidth={1.75} aria-hidden="true" className="sm:mr-1.5" />
            <span
              lang={locale === 'kn' ? 'en' : 'kn'}
              className={`${locale === 'kn' ? '' : 'kn'} hidden font-medium sm:inline leading-none`}
            >
              {locale === 'kn' ? 'English' : 'ಕನ್ನಡ'}
            </span>
          </button>

          {/* Theme toggle: Light / Dark */}
          <button
            type="button"
            onClick={onToggleTheme}
            aria-label={theme === 'dark' ? t('nav.light') : t('nav.dark')}
            aria-pressed={theme === 'dark'}
            className="inline-flex h-11 w-11 items-center justify-center rounded-control text-ink-soft transition-colors hover:text-indigo"
          >
            {theme === 'dark' ? (
              <Sun size={20} strokeWidth={1.75} aria-hidden="true" />
            ) : (
              <Moon size={20} strokeWidth={1.75} aria-hidden="true" />
            )}
          </button>
        </div>
      </div>

      <KasutiBorder />
    </header>
  );
}
