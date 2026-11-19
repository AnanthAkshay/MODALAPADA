import React, { createContext, useCallback, useContext, useMemo } from 'react';
import { COPY } from './strings';

const KANNADA_DIGITS = '೦೧೨೩೪೫೬೭೮೯';
const STORAGE_KEY = 'gaade_locale';

export function readLocale() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === 'kn' || stored === 'en') return stored;
  } catch (_) {
    /* storage unavailable */
  }
  return 'kn';
}

export function writeLocale(locale) {
  try {
    localStorage.setItem(STORAGE_KEY, locale);
  } catch (_) {
    /* storage unavailable */
  }
}

function lookup(path) {
  return path.split('.').reduce((node, key) => (node && node[key] !== undefined ? node[key] : undefined), COPY);
}

function interpolate(template, vars) {
  if (!template) return '';
  if (!vars) return template;
  return template.replace(/\{(\w+)\}/g, (match, name) => (vars[name] === undefined ? match : String(vars[name])));
}

const noopContext = {
  locale: 'kn',
  other: 'en',
  t: (path) => interpolate(lookup(path)?.kn, undefined),
  sub: (path) => interpolate(lookup(path)?.en, undefined),
  num: (value) => String(value),
  digits: (value) => String(value),
  themeName: (name) => name,
  themeSub: (name) => name,
};

const LocaleContext = createContext(noopContext);

export function LocaleProvider({ locale, children }) {
  const other = locale === 'kn' ? 'en' : 'kn';

  const value = useMemo(() => {
    const formatter =
      locale === 'kn'
        ? new Intl.NumberFormat('kn-IN-u-nu-knda')
        : new Intl.NumberFormat('en-IN');

    const digits = (input) =>
      locale === 'kn'
        ? String(input).replace(/[0-9]/g, (digit) => KANNADA_DIGITS[Number(digit)])
        : String(input);

    return {
      locale,
      other,
      t: (path, vars) => interpolate(lookup(path)?.[locale], vars),
      sub: (path, vars) => interpolate(lookup(path)?.[other], vars),
      num: (input) => formatter.format(input),
      digits,
      // Theme names arrive from the API in English; show Kannada first.
      themeName: (name) => lookup(`themeNames.${name}`)?.[locale] || name,
      themeSub: (name) => lookup(`themeNames.${name}`)?.[other] || name,
    };
  }, [locale, other]);

  return <LocaleContext.Provider value={value}>{children}</LocaleContext.Provider>;
}

export function useCopy() {
  return useContext(LocaleContext);
}

/**
 * Kannada primary line with the English line at ~80% beneath it.
 * Inherits size/colour from the caller.
 */
export function Bi({ k, vars, className = '', primaryClass = '', secondaryClass = 'text-meta text-ink-soft' }) {
  const { locale, other, t, sub } = useCopy();

  return (
    <span className={`flex flex-col ${className}`}>
      <span lang={locale} className={primaryClass}>
        {t(k, vars)}
      </span>
      <span lang={other} className={secondaryClass}>
        {sub(k, vars)}
      </span>
    </span>
  );
}

/** Primary line only, for places where a second line would break the layout. */
export function usePrimary() {
  const { t } = useCopy();
  return useCallback((key, vars) => t(key, vars), [t]);
}
