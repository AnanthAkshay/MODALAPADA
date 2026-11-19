// The five situations offered on the home screen.
// Labels live in src/i18n/{kn,en}.json (example.one … example.five).
// Bilingual payloads sent to /api/match depending on current site language.
export const EXAMPLES = [
  {
    id: 'starter-1',
    labelKey: 'one',
    situation:
      'Meena earns a modest salary as an entry-level clerk. However, she took a large personal loan to buy an expensive smartphone on EMI, and now struggles to pay her monthly rent and groceries.',
    situation_kn:
      'ಮೀನಾ ಸಣ್ಣ ಸಂಬಳದ ಗುಮಾಸ್ತೆ. ಆದರೆ ಆಡಂಬರಕ್ಕಾಗಿ ದುಬಾರಿ ಸ್ಮಾರ್ಟ್‌ಫೋನ್ ಅನ್ನು ಸಾಲ ಮಾಡಿ EMI ಮೇಲೆ ಖರೀದಿಸಿದಳು. ಈಗ ಮನೆ ಬಾಡಿಗೆ ಮತ್ತು ದಿನಸಿ ತರಲು ಪರದಾಡುತ್ತಿದ್ದಾಳೆ.',
  },
  {
    id: 'starter-2',
    labelKey: 'two',
    situation:
      'Municipal authorities ignored clearing clogged stormwater drains all summer. When torrential monsoon rains lashed the city and inundated residential basements, they frantically scrambled to deploy emergency diesel suction pumps.',
    situation_kn:
      'ಬೇಸಿಗೆಯಲ್ಲೆಲ್ಲಾ ನಗರಸಭೆ ರಾಜಕಾಲುವೆಗಳ ಹೂಳೆತ್ತದೆ ನಿರ್ಲಕ್ಷ್ಯ ಮಾಡಿತು. ಈಗ ಮುಂಗಾರು ಮಳೆ ಬಂದು ಮನೆಗಳ ತಳಮಹಡಿಗೆ ನೀರು ನುಗ್ಗಿದಾಗ, ತುರ್ತಾಗಿ ಪಂಪ್ ತಂದು ನೀರೆತ್ತಲು ಪರದಾಡುತ್ತಿದ್ದಾರೆ.',
  },
  {
    id: 'starter-3',
    labelKey: 'three',
    situation:
      'Shruti felt depressed seeing glamorous vacation photos of influencers on social media, assuming everyone else had flawless, effortless lives. Her grandmother reminded her that behind closed doors, every family contends with private heartaches, unpaid bills, and difficult conflicts.',
    situation_kn:
      'ಸಾಮಾಜಿಕ ಜಾಲತಾಣಗಳಲ್ಲಿ ಇತರರ ವೈಭವದ ಫೋಟೋಗಳನ್ನು ನೋಡಿ ಶ್ರುತಿಗೆ ಬೇಸರವಾಯಿತು. ಎಲ್ಲರ ಜೀವನ ಸುಖವಾಗಿದೆ ಎಂದುಕೊಂಡಳು. ಆದರೆ ಮನೆಯ ಗುಟ್ಟು ರಟ್ಟಾಗದಂತೆ ಎಲ್ಲರ ಮನೆಯಲ್ಲೂ ಒಂದಿಲ್ಲೊಂದು ಕಷ್ಟ, ನೋವು ಇರುತ್ತದೆ ಎಂದು ಅವಳ ಅಜ್ಜಿ ತಿಳಿಹೇಳಿದರು.',
  },
  {
    id: 'starter-4',
    labelKey: 'four',
    situation:
      'After sweating for months in high humidity pollinating vanilla orchid vines by hand, the young agriculturalist secured lucrative harvest contracts from organic bakeries.',
    situation_kn:
      'ತಿಂಗಳುಗಟ್ಟಲೆ ಬಿಸಿಲು-ಮಳೆಯೆನ್ನದೆ ಕಷ್ಟಪಟ್ಟು ವೆನಿಲ್ಲಾ ಬಳ್ಳಿಗಳನ್ನು ಸಾಕಿ ಹೂವು ಬಿಡಿಸಿದ ಯುವ ರೈತನಿಗೆ, ಈಗ ಸಾವಯವ ಬೇಕರಿಗಳಿಂದ ಒಳ್ಳೆಯ ದರದಲ್ಲಿ ಸುಗ್ಗಿ ಒಪ್ಪಂದ ಸಿಕ್ಕಿತು.',
  },
  {
    id: 'starter-5',
    labelKey: 'five',
    situation:
      'Hurrying to leave for the weekend bus, the research fellow poured reagent too rapidly into the beaker, causing a volatile chemical boil-over that ruined weeks of samples.',
    situation_kn:
      'ವಾರಾಂತ್ಯಕ್ಕೆ ಊರಿಗೆ ಹೊರಡಲು ಧಾವಂತದಲ್ಲಿದ್ದ ಸಂಶೋಧಕನು ಬೀಕರ್‌ಗೆ ರಾಸಾಯನಿಕವನ್ನು ಅವಸರದಿಂದ ಸುರಿದನು; ಇದರಿಂದ ರಿಯಾಕ್ಷನ್ ಹೊಗೆಯಾಡಿ ವಾರಗಳ ಪರಿಶ್ರಮ ಹಾಳಾಯಿತು.',
  },
];
