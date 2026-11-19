// One filled style (kumkum), one outline style, one text style.
// Every control is at least 44px tall for touch.

export const btnPrimary =
  'inline-flex min-h-[44px] items-center justify-center gap-2 rounded-control bg-kumkum px-5 text-body font-medium text-on-kumkum transition-colors hover:bg-kumkum-hover disabled:cursor-not-allowed disabled:bg-paper-deep disabled:text-ink-soft';

export const btnSecondary =
  'inline-flex min-h-[44px] items-center justify-center gap-2 rounded-control border border-line bg-paper px-5 text-body font-medium text-ink transition-colors hover:border-indigo hover:bg-paper-deep disabled:cursor-not-allowed disabled:opacity-45';

export const btnText =
  'inline-flex min-h-[44px] items-center gap-2 rounded-control text-body text-indigo underline-offset-4 transition-colors hover:underline disabled:cursor-not-allowed disabled:text-ink-soft disabled:no-underline';

export const btnIcon =
  'inline-flex h-11 w-11 shrink-0 items-center justify-center rounded-control border border-line text-ink transition-colors hover:border-indigo hover:bg-paper-deep';
