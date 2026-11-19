import React, { useState, useEffect, useRef } from 'react';
import { Send } from 'lucide-react';
import Header from './components/Header';
import StarterChips from './components/StarterChips';
import ChatMessage from './components/ChatMessage';
import LoadingSkeleton from './components/LoadingSkeleton';
import VoiceInput from './components/VoiceInput';
import ConsentModal from './components/ConsentModal';

export default function App() {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isConsentOpen, setIsConsentOpen] = useState(false);
  const [backendHealth, setBackendHealth] = useState({ status: 'checking', gaades_count: 0 });
  const [lastQuery, setLastQuery] = useState(null);
  const [debugInfo, setDebugInfo] = useState({ backend: null, lang: null, latency: null, status: 'idle' });
  const [autoPlay, setAutoPlay] = useState(() => {
    try {
      return localStorage.getItem('gaade_autoplay') === 'true';
    } catch (_) {
      return false;
    }
  });

  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  const API_BASE = import.meta.env.VITE_API_BASE_URL || '';
  const showDebug = typeof window !== 'undefined' && window.location.search.includes('debug=1');

  const handleToggleAutoPlay = () => {
    setAutoPlay((prev) => {
      const next = !prev;
      try {
        localStorage.setItem('gaade_autoplay', String(next));
      } catch (_) {}
      return next;
    });
  };

  // Check health on mount & set initial welcome message
  useEffect(() => {
    fetch(`${API_BASE}/health`)
      .then((res) => res.json())
      .then((data) => setBackendHealth(data))
      .catch((err) => {
        console.warn('Backend health check error:', err);
        setBackendHealth({ status: 'offline', message: 'Backend unreachable' });
      });

    // Initial Welcome Message
    setMessages([
      {
        id: 'welcome-1',
        sender: 'bot',
        type: 'notice',
        data: {
          status: 'greeting',
          message:
            'Welcome to Gaade Kosha (ಗಾದೆ ಕೋಶ). Describe any real-world situation, personal dilemma, or everyday observation in Kannada, English, or Kanglish, and I will match it with authentic Kannada proverb wisdom and original human audio recordings.'
        },
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ]);
  }, [API_BASE]);

  // Auto-scroll to latest message
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isLoading]);

  const handleSend = async (textToSend) => {
    const query = (textToSend || inputText).trim();
    if (!query || isLoading) return;

    const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // Add user message
    const userMsg = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: query,
      time: currentTime
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputText('');
    setIsLoading(true);
    setLastQuery(query);

    const startTime = performance.now();

    try {
      const response = await fetch(`${API_BASE}/api/match`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          text: query,
          lang: 'auto'
        })
      });

      const elapsedMs = Math.round(performance.now() - startTime);

      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();

      setDebugInfo({
        backend: result.matcher_backend || 'unknown',
        lang: result.detected_lang || 'unknown',
        latency: elapsedMs,
        status: result.status
      });

      let botMsgType = 'proverb';
      if (result.status === 'ambiguous') {
        botMsgType = 'ambiguous';
      } else if (
        result.status === 'no_good_match' ||
        result.status === 'greeting' ||
        result.status === 'invalid_input' ||
        result.status === 'inappropriate_input'
      ) {
        botMsgType = 'notice';
      }

      const botMsg = {
        id: `bot-${Date.now()}`,
        sender: 'bot',
        type: botMsgType,
        data: result,
        backend: result.matcher_backend,
        autoPlay: autoPlay,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      console.error('Match API Error:', err);
      const elapsedMs = Math.round(performance.now() - startTime);

      setDebugInfo({
        backend: 'error',
        lang: 'none',
        latency: elapsedMs,
        status: 'network_error'
      });

      const errorMsg = {
        id: `bot-err-${Date.now()}`,
        sender: 'bot',
        type: 'notice',
        data: {
          status: 'network_error',
          message:
            'Could not communicate with the Gaade Kosha backend server. Please make sure the backend is running on http://127.0.0.1:8000.'
        },
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRetryLast = () => {
    if (lastQuery) {
      handleSend(lastQuery);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="app-container">
      {/* Top Header with Auto-play Toggle and Consent Modal Trigger */}
      <Header
        backendHealth={backendHealth}
        autoPlay={autoPlay}
        onToggleAutoPlay={handleToggleAutoPlay}
        onOpenConsent={() => setIsConsentOpen(true)}
      />

      {/* Contributor & Developer Consent Declarations Modal */}
      <ConsentModal
        isOpen={isConsentOpen}
        onClose={() => setIsConsentOpen(false)}
      />

      {/* Main Chat Stream Container */}
      <main className="chat-window" role="log" aria-live="polite">
        <div className="messages-stream">
          {messages.map((msg) => (
            <ChatMessage key={msg.id} message={msg} onRetry={handleRetryLast} />
          ))}

          {isLoading && <LoadingSkeleton />}
          <div ref={messagesEndRef} />
        </div>
      </main>

      {/* Starter Chips Row */}
      <section className="chips-section" aria-label="Suggested starter queries">
        <StarterChips onSelectChip={(text) => handleSend(text)} disabled={isLoading} />
      </section>

      {/* Bottom Sticky Input Bar */}
      <footer className="input-bar-container">
        <form
          className="input-form"
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
        >
          {/* Live Web Speech API Voice Input with Hosted ASR Fallback */}
          <VoiceInput
            onTranscriptChange={(newText) => setInputText(newText)}
            currentText={inputText}
            disabled={isLoading}
            apiBase={API_BASE}
          />

          {/* Situation Textarea (Editable before sending) */}
          <textarea
            ref={textareaRef}
            className="situation-textarea kannada-text"
            rows={1}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="ಸಂದರ್ಭವನ್ನು ವಿವರಿಸಿ ಅಥವಾ ಮಾತನಾಡಿ... Describe or speak in Kannada, English, or Kanglish"
            disabled={isLoading}
            aria-label="Situation description input"
          />

          {/* Send Button */}
          <button
            type="submit"
            className="icon-btn send-btn"
            disabled={!inputText.trim() || isLoading}
            aria-label="Send situation description"
            title="Send query (Enter)"
          >
            <Send size={18} />
          </button>
        </form>

        {/* Small Hidden Debug Line (toggled via ?debug=1) */}
        {showDebug && (
          <div className="debug-banner" role="status">
            <span className="debug-pill">DEBUG MODE (?debug=1)</span>
            <span>Backend: <strong>{debugInfo.backend || 'none'}</strong></span>
            <span>Lang: <strong>{debugInfo.lang || 'none'}</strong></span>
            <span>Status: <strong>{debugInfo.status}</strong></span>
            {debugInfo.latency !== null && <span>Latency: <strong>{debugInfo.latency}ms</strong></span>}
          </div>
        )}
      </footer>
    </div>
  );
}
