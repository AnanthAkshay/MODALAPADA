import React, { useMemo } from 'react';

let kasutiCount = 0;

// Straight-stitch geometry only: right angles, diagonal steps, short dashes.
const GOPURA = 'M4 17H24 M6 17V12H22V17 M9 12V8H19V12 M12 8V5H16V8 M14 5V3';
const PALANQUIN = 'M32 16H60 M37 16V10H55V16 M40 10V7H52V10 M43 7V5H49V7 M46 5V3';
const LOTUS = 'M67 17H87 M77 15L70 11.5L77 8L84 11.5Z M77 13L73.5 11.5L77 10L80.5 11.5Z M70 11.5L67 9 M84 11.5L87 9 M77 8V5';
const LAMP = 'M96 17H120 M100 17V13H116V17 M108 13V10 M108 4L111.5 7L108 10L104.5 7Z M96 14H100 M116 14H120';

/**
 * Kasuti-inspired border: gopura, palanquin, lotus and lamp stitched onto a
 * 1px indigo baseline. Used in exactly three places: under the top bar,
 * between the gaade and its explanation, above the footer.
 */
export default function KasutiBorder({ className = '' }) {
  const patternId = useMemo(() => `kasuti-${(kasutiCount += 1)}`, []);

  return (
    <svg
      width="100%"
      height="20"
      className={className}
      aria-hidden="true"
      focusable="false"
      shapeRendering="crispEdges"
    >
      <defs>
        <pattern id={patternId} width="128" height="20" patternUnits="userSpaceOnUse">
          <line x1="0" y1="19.5" x2="128" y2="19.5" stroke="var(--indigo)" strokeWidth="1" />
          <path d={GOPURA} fill="none" stroke="var(--kumkum)" strokeWidth="1" />
          <path d={PALANQUIN} fill="none" stroke="var(--turmeric)" strokeWidth="1" />
          <path d={LOTUS} fill="none" stroke="var(--kumkum)" strokeWidth="1" />
          <path d={LAMP} fill="none" stroke="var(--turmeric)" strokeWidth="1" />
        </pattern>
      </defs>
      <rect width="100%" height="20" fill={`url(#${patternId})`} />
    </svg>
  );
}
