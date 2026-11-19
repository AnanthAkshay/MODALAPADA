import React, { createContext, useCallback, useContext, useMemo } from 'react';
import knData from './kn.json';
import enData from './en.json';

const DICTIONARIES = {
  kn: knData,
  en: enData,
};

const KANNADA_DIGITS = '೦೧೨೩೪೫೬೭೮೯';
const STORAGE_KEY = 'gaade_locale';

/**
 * Default language = Kannada if navigator.language starts with "kn", otherwise English.
 * Follows explicitly stored choice in localStorage if present.
 */
export function readLocale() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === 'kn' || stored === 'en') return stored;
  } catch (_) {
    /* storage unavailable */
  }
  if (typeof navigator !== 'undefined' && navigator.language) {
    return navigator.language.toLowerCase().startsWith('kn') ? 'kn' : 'en';
  }
  return 'en';
}

export function writeLocale(locale) {
  try {
    localStorage.setItem(STORAGE_KEY, locale);
  } catch (_) {
    /* storage unavailable */
  }
}

function lookup(dict, path) {
  if (!dict || !path) return undefined;
  return path.split('.').reduce((node, key) => (node && node[key] !== undefined ? node[key] : undefined), dict);
}

function interpolate(template, vars) {
  if (!template) return '';
  if (!vars) return template;
  return template.replace(/\{(\w+)\}/g, (match, name) => (vars[name] === undefined ? match : String(vars[name])));
}

const noopContext = {
  locale: 'kn',
  other: 'en',
  t: (path, vars) => interpolate(lookup(DICTIONARIES.kn, path), vars) || path,
  sub: (path, vars) => interpolate(lookup(DICTIONARIES.en, path), vars) || '',
  num: (value) => String(value),
  digits: (value) => String(value),
  themeName: (name) => lookup(DICTIONARIES.kn, `themeNames.${name}`) || name,
  themeSub: (name) => lookup(DICTIONARIES.en, `themeNames.${name}`) || name,
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

    const activeDict = DICTIONARIES[locale] || DICTIONARIES.en;
    const secondaryDict = DICTIONARIES[other] || DICTIONARIES.kn;

    return {
      locale,
      other,
      t: (path, vars) => {
        const val = lookup(activeDict, path);
        return val !== undefined ? interpolate(val, vars) : path;
      },
      sub: (path, vars) => {
        const val = lookup(secondaryDict, path);
        return val !== undefined ? interpolate(val, vars) : '';
      },
      num: (input) => formatter.format(input),
      digits,
      // Theme names arrive from the API in English; show Kannada or English as per locale
      themeName: (name) => lookup(activeDict, `themeNames.${name}`) || name,
      themeSub: (name) => lookup(secondaryDict, `themeNames.${name}`) || name,
    };
  }, [locale, other]);

  return <LocaleContext.Provider value={value}>{children}</LocaleContext.Provider>;
}

export function useCopy() {
  return useContext(LocaleContext);
}

/**
 * Primary line in active site language with the secondary line at ~80% beneath it.
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
