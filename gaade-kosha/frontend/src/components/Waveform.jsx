import React from 'react';

const BARS = [6, 12, 9, 15, 8];
const BAR_HEIGHT = [7, 14, 9, 16, 8];

/** Flat waveform bars; static unless audio is playing. */
export default function Waveform({ playing = false, className = '' }) {
  return (
    <span
      aria-hidden="true"
      className={`inline-flex h-4 items-center gap-[3px] ${className}`}
    >
      {Array.from({ length: playing ? BARS.length : 3 }).map((_, index) => (
        <span
          key={index}
          className={`w-[2px] rounded-full bg-current ${playing ? 'animate-wave-bar motion-reduce:animate-none' : ''}`}
          style={{
            height: `${playing ? BAR_HEIGHT[index] : 4 + (index % 2) * 4}px`,
            animationDelay: `${index * 110}ms`,
            transformOrigin: 'center',
          }}
        />
      ))}
    </span>
  );
}
