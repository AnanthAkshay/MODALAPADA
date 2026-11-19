import React from 'react';
import { SearchX, Sparkles, AlertTriangle, MessageSquare, RefreshCw } from 'lucide-react';

export default function NoticeCard({ status, message, onRetry }) {
  if (status === 'no_good_match') {
    return (
      <div className="notice-card no-match">
        <div className="notice-icon">
          <SearchX size={26} />
        </div>
        <div className="notice-content">
          <h3 className="notice-title kannada-text">
            ಯಾವುದೇ ಗಾದೆ ಹೊಂದಿಕೆಯಾಗಲಿಲ್ಲ (No Close Proverb Found)
          </h3>
          <p className="notice-text">
            {message ||
              'No Kannada proverb in our 226-proverb oral collection closely matched this description. Try adding specific actions, dilemmas, conflicts, or real-life outcomes to help us find the right folk wisdom.'}
          </p>
          <div className="notice-tip">
            💡 <em>ಸಲಹೆ (Tip): Describe a specific event — for example, someone acting in haste, being greedy, or working hard on a farm.</em>
          </div>
        </div>
      </div>
    );
  }

  if (status === 'greeting') {
    return (
      <div className="notice-card greeting">
        <div className="notice-icon">
          <Sparkles size={26} />
        </div>
        <div className="notice-content">
          <h3 className="notice-title kannada-text">
            ನಮಸ್ಕಾರ! Namaskara!
          </h3>
          <p className="notice-text">
            {message ||
              'Welcome to Gaade Kosha (ಗಾದೆ ಕೋಶ). Describe any real-world situation, personal dilemma, or everyday observation in Kannada, English, or Kanglish, and I will match it with authentic Kannada proverb wisdom and original human audio recordings.'}
          </p>
          <div className="notice-tip">
            👉 <em>Try clicking one of the starter situations below to explore how it works!</em>
          </div>
        </div>
      </div>
    );
  }

  if (status === 'inappropriate_input') {
    return (
      <div className="notice-card warning">
        <div className="notice-icon">
          <AlertTriangle size={24} />
        </div>
        <div className="notice-content">
          <h3 className="notice-title">
            Inappropriate Content Detected
          </h3>
          <p className="notice-text">
            {message ||
              'The input contains abusive or inappropriate language. Gaade Kosha is a cultural heritage archive. Please describe a genuine real-world scenario or life lesson.'}
          </p>
        </div>
      </div>
    );
  }

  if (status === 'invalid_input') {
    return (
      <div className="notice-card info">
        <div className="notice-icon">
          <MessageSquare size={24} />
        </div>
        <div className="notice-content">
          <h3 className="notice-title">
            Description Too Short · ವಿವರಣೆ ಸಾಲದು
          </h3>
          <p className="notice-text">
            {message ||
              'Please provide a bit more description (at least a sentence or two) about what happened, so the semantic matcher can identify the underlying moral.'}
          </p>
        </div>
      </div>
    );
  }

  if (status === 'network_error' || status === 'error') {
    return (
      <div className="notice-card error">
        <div className="notice-icon">
          <AlertTriangle size={24} />
        </div>
        <div className="notice-content">
          <h3 className="notice-title">
            ಸಂಪರ್ಕ ದೋಷ (Connection Error)
          </h3>
          <p className="notice-text">
            {message || 'Unable to connect to the Gaade Kosha backend server. Please verify the service is running.'}
          </p>
          {onRetry && (
            <button type="button" className="retry-btn" onClick={onRetry} aria-label="Retry query">
              <RefreshCw size={15} />
              <span>ಪುನಃ ಪ್ರಯತ್ನಿಸಿ (Retry)</span>
            </button>
          )}
        </div>
      </div>
    );
  }

  return null;
}

