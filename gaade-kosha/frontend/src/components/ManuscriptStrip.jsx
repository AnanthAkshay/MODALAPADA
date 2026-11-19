import React from 'react';

/**
 * The gaade sits on a palm-leaf (ಓಲೆಗರಿ) strip: flat warm panel, darker 1px
 * border, two punched binding holes. No gradient, no shadow.
 */
export default function ManuscriptStrip({ item }) {
  return (
    <div className="relative rounded-surface border border-line bg-paper-deep px-7 py-9 sm:px-14 sm:py-12">
      <span
        aria-hidden="true"
        className="absolute left-2.5 top-1/2 h-3 w-3 -translate-y-1/2 rounded-full border border-line bg-paper"
      />
      <span
        aria-hidden="true"
        className="absolute right-2.5 top-1/2 h-3 w-3 -translate-y-1/2 rounded-full border border-line bg-paper"
      />

      <div className="text-center">
        <h2
          lang="kn"
          className="kn-serif mx-auto max-w-[16ch] break-words text-gaade font-bold leading-[1.7] text-indigo wrap-balance"
        >
          {item.gaade}
        </h2>

        {item.english ? (
          <p
            lang="en"
            className="mx-auto mt-4 max-w-[42ch] text-body italic leading-[1.7] text-ink-soft"
          >
            {item.english}
          </p>
        ) : null}
      </div>
    </div>
  );
}
