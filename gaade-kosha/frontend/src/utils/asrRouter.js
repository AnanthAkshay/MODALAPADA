/**
 * ASR Routing Logic for Gaade Kosha
 * Determines whether to use native browser SpeechRecognition or hosted ASR fallback.
 */

export function determineAsrRoute({
  hasNativeSpeech = false,
  isBrave = false,
  sessionForceFallback = false,
  lastNativeError = null
}) {
  // 1. If remembered from previous session switch, stay on fallback
  if (sessionForceFallback) {
    return {
      route: 'fallback',
      reason: 'session_forced',
      friendlyNotice: null
    };
  }

  // 2. Brave blocks Google Speech API server endpoint -> direct fallback
  if (isBrave) {
    return {
      route: 'fallback',
      reason: 'brave_browser',
      friendlyNotice: null
    };
  }

  // 3. Browser lacks native SpeechRecognition implementation (e.g. Firefox, older Safari)
  if (!hasNativeSpeech) {
    return {
      route: 'fallback',
      reason: 'native_unsupported',
      friendlyNotice: null
    };
  }

  // 4. Native recognition fired a network or service-not-allowed error -> switch to fallback
  if (lastNativeError === 'network' || lastNativeError === 'service-not-allowed') {
    return {
      route: 'fallback',
      reason: 'native_network_error',
      friendlyNotice: "Your browser's built-in speech service isn't available, switching to the recorder."
    };
  }

  // 5. Default: Chrome / Edge native Web Speech API
  return {
    route: 'native',
    reason: 'native_available',
    friendlyNotice: null
  };
}

