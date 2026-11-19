import React from 'react';
import { Globe, Moon, Sun } from 'lucide-react';
import { useCopy } from '../i18n';
import KasutiBorder from './KasutiBorder';

export default function TopBar({ view, onNavigate, theme, onToggleTheme, locale, onToggleLocale, status }) {
  const { t, sub } = useCopy();

  return (
    <header>
      <div className="mx-auto flex min-h-[72px] max-w-content items-center gap-2 px-4 py-2 sm:px-8">
        <button
          type="button"
          onClick={() => onNavigate('home')}
          aria-current={view === 'home' ? 'page' : undefined}
          className="flex shrink-0 flex-col items-start rounded-control py-1"
        >
          <span lang="kn" className="kn text-[24px] font-semibold leading-[1.15] text-ink sm:text-[28px]">
            {t('brand')}
          </span>
          <span lang="en" className="text-[12px] leading-tight text-ink-soft">
            {sub('brand')}
          </span>
        </button>

        <div className="ml-auto flex items-center gap-0 sm:gap-1">
          {status ? (
            <span className="mr-1 hidden items-center gap-1.5 text-meta text-kumkum md:inline-flex">
              <span aria-hidden="true" className="h-1.5 w-1.5 rounded-full bg-kumkum" />
              <span lang="kn" className="kn leading-[1.7]">
                {t('nav.unreachable')}
              </span>
            </span>
          ) : null}

          <button
            type="button"
            onClick={() => onNavigate('browse')}
            aria-current={view === 'browse' ? 'page' : undefined}
            className={`inline-flex min-h-[44px] flex-col justify-center rounded-control px-2 text-left transition-colors hover:text-indigo sm:px-3 ${
              view === 'browse' ? 'text-indigo' : 'text-ink'
            }`}
          >
            <span lang="kn" className="kn whitespace-nowrap text-[13px] leading-[1.5] sm:text-body">
              {t('nav.browse')}
            </span>
            <span lang="en" className="hidden text-[11px] leading-tight text-ink-soft sm:block">
              {sub('nav.browse')}
            </span>
          </button>

          <button
            type="button"
            onClick={onToggleLocale}
            aria-label={locale === 'kn' ? t('nav.switchToEnglish') : t('nav.switchToKannada')}
            className="inline-flex h-11 min-w-[44px] items-center justify-center rounded-control px-1.5 text-meta text-ink-soft transition-colors hover:text-indigo"
          >
            <Globe size={18} strokeWidth={1.75} aria-hidden="true" className="sm:hidden" />
            <span lang={locale === 'kn' ? 'en' : 'kn'} className="kn hidden leading-none sm:inline">
              {locale === 'kn' ? 'English' : 'ಕನ್ನಡ'}
            </span>
          </button>

          <button
            type="button"
            onClick={onToggleTheme}
            aria-label={theme === 'dark' ? t('nav.light') : t('nav.dark')}
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
