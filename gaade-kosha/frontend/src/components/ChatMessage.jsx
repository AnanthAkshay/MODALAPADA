import React from 'react';
import { User, Sparkles } from 'lucide-react';
import ProverbCard from './ProverbCard';
import AmbiguousCard from './AmbiguousCard';
import NoticeCard from './NoticeCard';

export default function ChatMessage({ message, onRetry }) {
  const isUser = message.sender === 'user';

  if (isUser) {
    return (
      <div className="chat-row user-row">
        <div className="chat-bubble user-bubble">
          <p className="user-message-text">{message.text}</p>
          <div className="message-meta user-meta">
            <span className="message-time">{message.time}</span>
            <User size={12} />
          </div>
        </div>
      </div>
    );
  }

  // Bot response row
  return (
    <div className="chat-row bot-row">
      <div className="bot-avatar">
        <Sparkles size={16} />
      </div>

      <div className="chat-bubble bot-bubble">
        {/* Proverb Match Result */}
        {message.type === 'proverb' && message.data && (
          <ProverbCard
            item={message.data.best}
            alternatives={message.data.alternatives}
            autoPlay={message.autoPlay || false}
          />
        )}

        {/* Ambiguous Response */}
        {message.type === 'ambiguous' && message.data && (
          <AmbiguousCard
            message={message.data.message}
            best={message.data.best}
            alternatives={message.data.alternatives}
          />
        )}

        {/* Notice Card: no match, greeting, invalid input, inappropriate, error */}
        {message.type === 'notice' && message.data && (
          <NoticeCard
            status={message.data.status}
            message={message.data.message}
            onRetry={onRetry}
          />
        )}

        <div className="message-meta bot-meta">
          <span className="message-time">{message.time}</span>
          {message.backend && (
            <span className="backend-tag">via {message.backend}</span>
          )}
        </div>
      </div>
    </div>
  );
}

