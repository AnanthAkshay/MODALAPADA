import React from 'react';
import KasutiBorder from './KasutiBorder';
import { useCopy } from '../i18n';

export default function SiteFooter({ gaadeCount, onOpenConsent }) {
  const { t, sub, other, num } = useCopy();

  return (
    <footer className="mt-auto">
      <KasutiBorder />

      <div className="mx-auto flex max-w-content flex-col gap-6 px-4 py-8 sm:flex-row sm:items-start sm:justify-between sm:px-8">
        <div className="min-w-0">
          <p lang="kn" className="kn-serif text-title font-bold leading-[1.7] text-ink">
            {t('footer.heritage')}
          </p>
          <p lang={other} className="text-meta leading-tight text-ink-soft">
            {sub('footer.heritage')}
          </p>

          <p className="mt-3 flex max-w-[46ch] flex-col text-meta text-ink-soft">
            <span lang="kn" className="kn leading-[1.7]">
              {gaadeCount ? `${t('footer.count', { count: num(gaadeCount) })} · ` : ''}
              {t('footer.recorded')}
            </span>
            <span lang={other} className="text-[12px] leading-tight">
              {gaadeCount ? `${sub('footer.count', { count: num(gaadeCount) })} · ` : ''}
              {sub('footer.recorded')}
            </span>
          </p>
        </div>

        <div className="flex shrink-0 flex-col items-start gap-2 sm:items-end">
          <button
            type="button"
            onClick={onOpenConsent}
            className="min-h-[44px] rounded-control text-left text-meta text-ink-soft underline-offset-4 transition-colors hover:text-indigo hover:underline sm:text-right"
          >
            <span lang="kn" className="kn block leading-[1.7]">
              {t('footer.consent')}
            </span>
            <span lang={other} className="block text-[12px] leading-tight">
              {sub('footer.consent')}
            </span>
          </button>

          <span className="text-[12px] leading-tight text-ink-soft">{t('footer.institution')}</span>
        </div>
      </div>
    </footer>
  );
}
