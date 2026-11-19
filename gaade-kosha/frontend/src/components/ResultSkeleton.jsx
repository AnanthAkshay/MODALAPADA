import React from 'react';
import { useCopy } from '../i18n';

export default function ResultSkeleton() {
  const { t } = useCopy();

  return (
    <div aria-busy="true" className="animate-pulse motion-reduce:animate-none">
      <p role="status" className="sr-only">
        {t('loading')}
      </p>

      <div className="rounded-surface border border-line bg-paper-deep px-7 py-9 sm:px-14 sm:py-12">
        <div className="mx-auto h-8 w-11/12 rounded bg-line" />
        <div className="mx-auto mt-4 h-8 w-8/12 rounded bg-line" />
        <div className="mx-auto mt-6 h-4 w-6/12 rounded bg-line" />
      </div>

      <div className="mt-9 flex flex-wrap justify-center gap-3">
        <div className="h-14 w-32 rounded-control bg-paper-deep" />
        <div className="h-14 w-44 rounded-control bg-paper-deep" />
      </div>

      <div className="mt-10 grid gap-8 border-t border-line pt-8 sm:grid-cols-2">
        {[0, 1].map((column) => (
          <div key={column} className="space-y-3">
            <div className="h-3 w-24 rounded bg-paper-deep" />
            <div className="h-4 w-full rounded bg-paper-deep" />
            <div className="h-4 w-11/12 rounded bg-paper-deep" />
            <div className="h-4 w-8/12 rounded bg-paper-deep" />
          </div>
        ))}
      </div>
    </div>
  );
}
