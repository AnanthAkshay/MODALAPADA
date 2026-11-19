import React from 'react';
import { Sparkles } from 'lucide-react';

export const STARTER_SCENARIOS = [
  {
    id: 'starter-1',
    icon: '📱',
    label: 'Smartphone on EMI',
    situation:
      'Meena earns a modest salary as an entry-level clerk. However, she took a large personal loan to buy an expensive smartphone on EMI, and now struggles to pay her monthly rent and groceries.'
  },
  {
    id: 'starter-2',
    icon: '🌧️',
    label: 'Clogged Storm Drains',
    situation:
      'Municipal authorities ignored clearing clogged stormwater drains all summer. When torrential monsoon rains lashed the city and inundated residential basements, they frantically scrambled to deploy emergency diesel suction pumps.'
  },
  {
    id: 'starter-3',
    icon: '✨',
    label: 'Social Media Glamour',
    situation:
      'Shruti felt depressed seeing glamorous vacation photos of influencers on social media, assuming everyone else had flawless, effortless lives. Her grandmother reminded her that behind closed doors, every family contends with private heartaches, unpaid bills, and difficult conflicts.'
  },
  {
    id: 'starter-4',
    icon: '🌾',
    label: 'Hard Work on Farmland',
    situation:
      'After sweating for months in high humidity pollinating vanilla orchid vines by hand, the young agriculturalist secured lucrative harvest contracts from organic bakeries.'
  },
  {
    id: 'starter-5',
    icon: '⏰',
    label: 'Last-Minute Rush Blunder',
    situation:
      'Hurrying to leave for the weekend bus, the research fellow poured reagent too rapidly into the beaker, causing a volatile chemical boil-over that ruined weeks of samples.'
  }
];

export default function StarterChips({ onSelectChip, disabled = false }) {
  return (
    <div className="starter-chips-container" aria-label="Starter situations">
      <div className="starter-chips-header">
        <Sparkles size={14} className="sparkle-icon" />
        <span>Try these real-life scenarios · ಉದಾಹರಣೆ ಸಂದರ್ಭಗಳು:</span>
      </div>
      <div className="chips-scroll-row">
        {STARTER_SCENARIOS.map((item) => (
          <button
            key={item.id}
            type="button"
            className="starter-chip"
            onClick={() => onSelectChip(item.situation)}
            disabled={disabled}
            aria-label={`Try scenario: ${item.label}`}
            title={item.situation}
          >
            <span className="chip-icon">{item.icon}</span>
            <span className="chip-label">{item.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

