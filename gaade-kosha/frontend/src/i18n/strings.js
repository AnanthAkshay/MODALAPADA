/**
 * Every visible string in the app, in one place.
 * Kannada is the primary line; English is the small secondary line.
 * Edit the Kannada here — components never hold copy.
 */
export const COPY = {
  brand: { kn: 'ಗಾದೆ ಕೋಶ', en: 'Gaade Kosha' },

  nav: {
    browse: { kn: 'ಎಲ್ಲಾ ಗಾದೆಗಳು', en: 'Browse' },
    skip: { kn: 'ಮುಖ್ಯ ಭಾಗಕ್ಕೆ ಹೋಗಿ', en: 'Skip to content' },
    switchToEnglish: { kn: 'ಇಂಗ್ಲಿಷ್‌ಗೆ ಬದಲಿಸಿ', en: 'Switch to English' },
    switchToKannada: { kn: 'ಕನ್ನಡಕ್ಕೆ ಬದಲಿಸಿ', en: 'Switch to Kannada' },
    light: { kn: 'ಬೆಳಕಿನ ನೋಟಕ್ಕೆ ಬದಲಿಸಿ', en: 'Switch to light appearance' },
    dark: { kn: 'ಕಪ್ಪು ನೋಟಕ್ಕೆ ಬದಲಿಸಿ', en: 'Switch to dark appearance' },
    unreachable: { kn: 'ಸಂಗ್ರಹ ಸಿಗುತ್ತಿಲ್ಲ', en: 'The archive is unreachable' },
  },

  home: {
    headline: { kn: 'ಯಾವ ಸಂದರ್ಭ?', en: 'What’s the situation?' },
    subline: {
      kn: 'ನಿಮ್ಮ ಪರಿಸ್ಥಿತಿ ಹೇಳಿ, ಸರಿಯಾದ ಗಾದೆ ಹುಡುಕುತ್ತೇವೆ.',
      en: 'Tell us what’s happening. We’ll find the gaade for it.',
    },
    placeholder: { kn: 'ನಿಮ್ಮ ಪರಿಸ್ಥಿತಿಯನ್ನು ಇಲ್ಲಿ ಬರೆಯಿರಿ…', en: 'Describe the situation…' },
    inputLabel: { kn: 'ನಿಮ್ಮ ಪರಿಸ್ಥಿತಿ', en: 'Your situation' },
    find: { kn: 'ಗಾದೆ ಹುಡುಕಿ', en: 'Find gaade' },
    speak: { kn: 'ಮಾತನಾಡಿ', en: 'Speak in' },
    micStart: { kn: 'ನಿಮ್ಮ ಪರಿಸ್ಥಿತಿ ಹೇಳಿ', en: 'Speak your situation' },
    micStop: { kn: 'ಧ್ವನಿ ನಿಲ್ಲಿಸಿ', en: 'Stop listening' },
    listening: { kn: 'ಕೇಳುತ್ತಿದ್ದೇವೆ…', en: 'Listening…' },
    speakNow: { kn: 'ಮಾತನಾಡಿ…', en: 'Speak now…' },
    transcriptHint: {
      kn: 'ಬರಹವನ್ನು ಸಂಪಾದಿಸಬಹುದು — ಕಳುಹಿಸುವ ಮೊದಲು ತಿದ್ದಿಕೊಳ್ಳಿ.',
      en: 'The transcript is editable — fix anything before you send it.',
    },
    examples: { kn: 'ಅಥವಾ ಇವುಗಳಲ್ಲಿ ಒಂದನ್ನು ಪ್ರಯತ್ನಿಸಿ', en: 'Or start from one of these' },
    voiceUnsupported: {
      kn: 'ಈ ಬ್ರೌಸರ್‌ನಲ್ಲಿ ಧ್ವನಿ ಬೆಂಬಲ ಇಲ್ಲ. ಪರಿಸ್ಥಿತಿಯನ್ನು ಬರೆಯಿರಿ.',
      en: 'Voice input isn’t available in this browser. Type the situation instead.',
    },
    dismiss: { kn: 'ಮುಚ್ಚಿ', en: 'Dismiss' },
  },

  example: {
    one: { kn: 'ಇಎಂಐ ಮೊಬೈಲ್', en: 'Smartphone on EMI' },
    two: { kn: 'ಕಟ್ಟಿದ ಚರಂಡಿ', en: 'Clogged storm drains' },
    three: { kn: 'ಸಾಮಾಜಿಕ ಜಾಲದ ಹೊಳಪು', en: 'Social media glamour' },
    four: { kn: 'ಹೊಲದ ಶ್ರಮ', en: 'Hard work on a farm' },
    five: { kn: 'ಕೊನೆ ಕ್ಷಣದ ಆತುರ', en: 'Last-minute rush' },
  },

  speech: {
    denied: {
      kn: 'ಮೈಕ್ರೊಫೋನ್ ಅನುಮತಿ ನಿರಾಕರಿಸಲಾಗಿದೆ. ಬ್ರೌಸರ್ ಸೆಟ್ಟಿಂಗ್‌ನಲ್ಲಿ ಅನುಮತಿ ಕೊಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.',
      en: 'Microphone permission was denied. Allow microphone access in your browser settings, then try again.',
    },
    'no-speech': {
      kn: 'ಮಾತು ಕೇಳಿಸಲಿಲ್ಲ. ಮೈಕ್ರೊಫೋನ್ ಹತ್ತಿರ ಮತ್ತೆ ಮಾತನಾಡಿ.',
      en: 'No speech was detected. Try again a little closer to the microphone.',
    },
    network: {
      kn: 'ಧ್ವನಿ ಗುರುತಿಸಲು ಇಂಟರ್ನೆಟ್ ಬೇಕು. ಸಂಪರ್ಕ ಪರಿಶೀಲಿಸಿ.',
      en: 'Speech recognition needs a network connection. Check your connection and try again.',
    },
    'audio-capture': {
      kn: 'ಈ ಸಾಧನದಲ್ಲಿ ಮೈಕ್ರೊಫೋನ್ ಸಿಗಲಿಲ್ಲ.',
      en: 'No microphone was found on this device.',
    },
    unsupported: {
      kn: 'ಈ ಬ್ರೌಸರ್‌ನಲ್ಲಿ ಧ್ವನಿ ಬೆಂಬಲ ಇಲ್ಲ.',
      en: 'Voice input is not available in this browser.',
    },
    unknown: {
      kn: 'ಧ್ವನಿ ಗುರುತಿಸುವಿಕೆ ನಿಂತುಹೋಯಿತು. ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.',
      en: 'Speech recognition stopped unexpectedly. Please try again.',
    },
  },

  poster: {
    label: { kn: 'ಕ್ಷಣದ ಗಾದೆ', en: 'Gaade of the moment' },
    fallbackGaade: { kn: 'ಕೈ ಕೆಸರಾದರೆ ಬಾಯಿ ಮೊಸರು.', en: 'No pain, no gain.' },
    play: { kn: 'ಕೇಳಿ', en: 'Play' },
  },

  result: {
    described: { kn: 'ನಿಮ್ಮ ಪರಿಸ್ಥಿತಿ', en: 'You described' },
    listen: { kn: 'ಕೇಳಿ', en: 'Listen' },
    pause: { kn: 'ನಿಲ್ಲಿಸಿ', en: 'Pause' },
    readExplanation: { kn: 'ವಿವರಣೆ ಓದಿ', en: 'Read explanation' },
    stopReading: { kn: 'ಓದುವುದನ್ನು ನಿಲ್ಲಿಸಿ', en: 'Stop reading' },
    machineVoice: { kn: 'ಯಂತ್ರ ಧ್ವನಿ', en: 'Machine voice' },
    noRecording: { kn: 'ಈ ಗಾದೆಗೆ ಧ್ವನಿ ಮುದ್ರಣ ಇಲ್ಲ', en: 'No recording for this gaade' },
    recordingFailed: { kn: 'ಮುದ್ರಣ ತೆರೆಯಲಾಗಲಿಲ್ಲ.', en: 'The recording didn’t load.' },
    retryAudio: { kn: 'ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ', en: 'Try again' },
    meaning: { kn: 'ಅರ್ಥ', en: 'Meaning' },
    whyItFits: { kn: 'ಏಕೆ ಹೊಂದುತ್ತದೆ', en: 'Why it fits' },
    theme: { kn: 'ವಿಷಯ', en: 'Theme' },
    themeUnverified: { kn: 'ವಿಷಯ ನಮೂದಿಸಿಲ್ಲ', en: 'Theme unverified' },
    regionUnverified: { kn: 'ಪ್ರದೇಶ ಪರಿಶೀಲಿಸಿಲ್ಲ', en: 'Region unverified' },
    region: { kn: 'ಪ್ರದೇಶ', en: 'Region' },
    alternative: { kn: 'ಪರ್ಯಾಯ {index} / {total}', en: 'Alternative {index} of {total}' },
    showAnother: { kn: 'ಇನ್ನೊಂದು ತೋರಿಸಿ', en: 'Show another match' },
    newSituation: { kn: 'ಹೊಸ ಸಂದರ್ಭ', en: 'New situation' },
    backToBrowse: { kn: 'ಎಲ್ಲಾ ಗಾದೆಗಳಿಗೆ ಹಿಂತಿರುಗಿ', en: 'Browse all gaades' },
    othersFit: { kn: 'ಬೇರೆ ಹೊಂದುವ ಗಾದೆಗಳು', en: 'The other gaades that fit' },
    ambiguous: { kn: 'ಹಲವು ಗಾದೆಗಳು ಹೊಂದುತ್ತವೆ.', en: 'A few gaades fit this situation.' },
    explanationForFirst: {
      kn: 'ವಿವರಣೆ ಹತ್ತಿರದ ಹೊಂದಿಕೆಗೆ ಮಾತ್ರ ಬರೆಯಲಾಗಿದೆ. ಮೊದಲ ಗಾದೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ.',
      en: 'An explanation is written for the closest match only. Choose the first gaade to read it.',
    },
    explanationFromBrowse: {
      kn: 'ಸಂದರ್ಭಕ್ಕೆ ಹೊಂದಿಸಿದಾಗ ಮಾತ್ರ ವಿವರಣೆ ಬರುತ್ತದೆ. ಈ ನಮೂದಿಗೆ ಇನ್ನೂ ಇಲ್ಲ.',
      en: 'An explanation is written when a gaade is matched to a situation, so this entry has none yet.',
    },
    notice: {
      no_good_match: { kn: 'ಖಚಿತ ಹೊಂದಿಕೆ ಸಿಗಲಿಲ್ಲ', en: 'No confident match' },
      invalid_input: { kn: 'ಸ್ವಲ್ಪ ಹೆಚ್ಚು ಬರೆಯಿರಿ', en: 'That’s a little short' },
      inappropriate_input: { kn: 'ಈ ಪಠ್ಯ ತಿರಸ್ಕೃತವಾಯಿತು', en: 'That input was rejected' },
      greeting: { kn: 'ನಮಸ್ಕಾರ', en: 'Namaskara' },
      error: { kn: 'ಹುಡುಕಾಟದಲ್ಲಿ ದೋಷ ಉಂಟಾಯಿತು', en: 'The matcher ran into a problem' },
      fallback: { kn: 'ಇನ್ನೂ ಹೊಂದಿಕೆ ಇಲ್ಲ', en: 'Nothing to match yet' },
    },
    noMatchTip: {
      kn: 'ಏನಾಯಿತು, ಅದರ ಪರಿಣಾಮ ಏನು, ಯಾರು ಒಳಗೊಂಡರು ಎಂದು ಬರೆಯಿರಿ. ನಿರ್ದಿಷ್ಟ ಕ್ರಿಯೆ ಸರಿಯಾದ ಗಾದೆ ತರುತ್ತದೆ.',
      en: 'Try describing what happened, what it cost, and who was involved. A concrete action usually brings the right gaade to the surface.',
    },
    describeAnother: { kn: 'ಬೇರೆ ಸಂದರ್ಭ ಹೇಳಿ', en: 'Describe another situation' },
    tryAgain: { kn: 'ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ', en: 'Try again' },
    errorNetworkTitle: { kn: 'ಸಂಗ್ರಹ ಉತ್ತರಿಸಲಿಲ್ಲ', en: 'The archive didn’t answer' },
    errorNetworkBody: {
      kn: 'ಹುಡುಕಾಟ ಸೇವೆ ಸಿಗುತ್ತಿಲ್ಲ. ಸೇವೆ ಚಾಲನೆಯಲ್ಲಿದೆಯೇ ಮತ್ತು ಸಂಪರ್ಕ ಇದೆಯೇ ಪರಿಶೀಲಿಸಿ — ನೀವು ಬರೆದದ್ದು ಉಳಿದಿದೆ.',
      en: 'The matcher service could not be reached. Check that the API is running and the connection is up — nothing you typed was lost.',
    },
    errorHttpTitle: { kn: 'ಸಂಗ್ರಹ ದೋಷ ಕೊಟ್ಟಿತು', en: 'The matcher returned an error' },
    errorHttpBody: {
      kn: 'ಹುಡುಕಾಟ HTTP {status} ಎಂದು ಉತ್ತರಿಸಿತು. ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ ಅಥವಾ ಬೇರೆ ರೀತಿಯಲ್ಲಿ ವಿವರಿಸಿ.',
      en: 'The matcher replied with HTTP {status}. Try again, or describe the situation in a different way.',
    },
    queryLabel: { kn: 'ಪ್ರಶ್ನೆ', en: 'Query' },
  },

  browse: {
    title: { kn: 'ಎಲ್ಲಾ ಗಾದೆಗಳು', en: 'Browse the collection' },
    intro: { kn: '{count} ಗಾದೆಗಳು, ಪ್ರತಿಯೊಂದೂ ಮನೆಯವರ ಧ್ವನಿಯಲ್ಲಿ.', en: '{count} gaades, each recorded by the person who keeps it.' },
    introPending: { kn: 'ಸಂಗ್ರಹದ ಎಲ್ಲಾ ಗಾದೆಗಳು, ಧ್ವನಿ ಸಹಿತ.', en: 'Every gaade in the collection, with its recording.' },
    search: { kn: 'ಗಾದೆ ಅಥವಾ ಅರ್ಥ ಹುಡುಕಿ', en: 'Search gaades and meanings' },
    allThemes: { kn: 'ಎಲ್ಲಾ ವಿಷಯಗಳು', en: 'All themes' },
    showAllThemes: { kn: 'ಎಲ್ಲಾ {count} ವಿಷಯಗಳನ್ನು ತೋರಿಸಿ', en: 'Show all {count} themes' },
    showFewerThemes: { kn: 'ಕಡಿಮೆ ವಿಷಯಗಳನ್ನು ತೋರಿಸಿ', en: 'Show fewer themes' },
    empty: { kn: '“{query}” ಗೆ ಯಾವುದೇ ಗಾದೆ ಸಿಗಲಿಲ್ಲ.', en: 'No gaades match “{query}”.' },
    clear: { kn: 'ಹುಡುಕಾಟ ತೆರವು ಮಾಡಿ', en: 'Clear the search' },
    loadError: {
      kn: 'ಸಂಗ್ರಹ ತೆರೆಯಲಾಗಲಿಲ್ಲ. ಸಂಪರ್ಕ ಪರಿಶೀಲಿಸಿ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.',
      en: 'The collection couldn’t be loaded. Check the connection and try again.',
    },
    loading: { kn: 'ಗಾದೆಗಳು ಬರುತ್ತಿವೆ…', en: 'Loading gaades…' },
  },

  footer: {
    heritage: { kn: 'ಹಿರಿಯರ ಮಾತು', en: 'Words of the elders' },
    count: { kn: '{count} ಕನ್ನಡ ಗಾದೆಗಳು', en: '{count} Kannada gaades' },
    recorded: { kn: 'ಇವನ್ನು ಕಾಪಾಡಿಕೊಂಡು ಬಂದ ಕುಟುಂಬಗಳ ಧ್ವನಿಯಲ್ಲಿ.', en: 'Recorded by the families who keep them.' },
    consent: { kn: 'ಒಪ್ಪಿಗೆ ಪತ್ರ', en: 'Consent declarations' },
    institution: { kn: 'ಮೊದಲಪದ ೨.೦ · ಆರ್‌ಐಟಿ ಸಿಎಸ್‌ಇ&ಇ', en: 'Modalapada 2.0 · RIT CSE&E' },
  },

  consent: {
    close: { kn: 'ಒಪ್ಪಿಗೆ ಪತ್ರ ಮುಚ್ಚಿ', en: 'Close consent declarations' },
    note: {
      kn: 'ಸಹಿ ಮಾಡಿದ ಘೋಷಣೆಗಳನ್ನು ಯೋಜನೆಯ ಸಲ್ಲಿಕೆಯೊಂದಿಗೆ ಸಂಗ್ರಹಿಸಲಾಗಿದೆ. ಧ್ವನಿ ಮತ್ತು ಪಠ್ಯ ಕೊಡುಗೆದಾರ ಕುಟುಂಬಗಳ ಬಳಿಯೇ ಉಳಿಯುತ್ತದೆ.',
      en: 'Signed declarations are archived with the project submission. Audio and text remain with the contributing families.',
    },
  },

  loading: { kn: 'ಹತ್ತಿರದ ಗಾದೆ ಹುಡುಕುತ್ತಿದ್ದೇವೆ…', en: 'Finding the closest gaade…' },

  // Theme names come from the API in English; these are the display names.
  themeNames: {
    Character: { kn: 'ಸ್ವಭಾವ', en: 'Character' },
    Society: { kn: 'ಸಮಾಜ', en: 'Society' },
    Money: { kn: 'ಹಣ', en: 'Money' },
    Time: { kn: 'ಸಮಯ', en: 'Time' },
    Work: { kn: 'ಕೆಲಸ', en: 'Work' },
    Family: { kn: 'ಕುಟುಂಬ', en: 'Family' },
    Friends: { kn: 'ಸ್ನೇಹ', en: 'Friends' },
    Study: { kn: 'ಅಧ್ಯಯನ', en: 'Study' },
    Health: { kn: 'ಆರೋಗ್ಯ', en: 'Health' },
    Leadership: { kn: 'ನಾಯಕತ್ವ', en: 'Leadership' },
    Agriculture: { kn: 'ಕೃಷಿ', en: 'Agriculture' },
    Business: { kn: 'ವ್ಯಾಪಾರ', en: 'Business' },
    Culture: { kn: 'ಸಂಸ್ಕೃತಿ', en: 'Culture' },
    Education: { kn: 'ಶಿಕ್ಷಣ', en: 'Education' },
    Nature: { kn: 'ಪ್ರಕೃತಿ', en: 'Nature' },
  },
};
