import React from 'react';

export default function LoadingSkeleton() {
  return (
    <div className="skeleton-card" aria-label="Loading proverb match" aria-busy="true">
      <div className="skeleton-badges">
        <div className="skeleton-line shimmer badge-pill"></div>
        <div className="skeleton-line shimmer badge-pill"></div>
        <div className="skeleton-line shimmer badge-pill"></div>
      </div>

      <div className="skeleton-header">
        <div className="skeleton-line shimmer gaade-line"></div>
        <div className="skeleton-line shimmer gaade-line-sub"></div>
        <div className="skeleton-line shimmer audio-btn-line"></div>
      </div>

      <div className="skeleton-sections">
        <div className="skeleton-section">
          <div className="skeleton-line shimmer label-line"></div>
          <div className="skeleton-line shimmer text-line"></div>
        </div>

        <div className="skeleton-section">
          <div className="skeleton-line shimmer label-line"></div>
          <div className="skeleton-line shimmer text-line"></div>
        </div>

        <div className="skeleton-section">
          <div className="skeleton-line shimmer label-line"></div>
          <div className="skeleton-line shimmer text-line"></div>
          <div className="skeleton-line shimmer text-line-short"></div>
        </div>
      </div>

      <div className="skeleton-footer">
        <div className="loading-spinner"></div>
        <span className="loading-caption kannada-text">
          ಗಾದೆ ಶೋಧಿಸಲಾಗುತ್ತಿದೆ... (Matching proverbs from 226 oral recordings)
        </span>
      </div>
    </div>
  );
}

