interface CombosProps {
  combosFiredToday: string[]
}

export default function Combos({ combosFiredToday }: CombosProps) {
  if (!combosFiredToday || combosFiredToday.length === 0) {
    return null
  }

  const getComboEmoji = (comboId: string): string => {
    const emojis: Record<string, string> = {
      morning_warrior: '🌅',
      deep_work_ultra: '🧠',
      perfect_day: '✨',
      fitness_fanatic: '💪',
      code_ninja: '🥷',
    }
    return emojis[comboId] || '🎉'
  }

  const getComboName = (comboId: string): string => {
    const names: Record<string, string> = {
      morning_warrior: 'Morning Warrior',
      deep_work_ultra: 'Deep Work Ultra',
      perfect_day: 'Perfect Day',
      fitness_fanatic: 'Fitness Fanatic',
      code_ninja: 'Code Ninja',
    }
    return names[comboId] || comboId.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
  }

  return (
    <div className="card-pixel mb-2">
      <h3 style={{ fontFamily: 'var(--font-mono)', fontSize: '0.875rem', marginBottom: 'var(--space-sm)' }}>
        🔥 Combos Fired Today
      </h3>
      <div className="flex gap-1 flex-col">
        {combosFiredToday.map((comboId) => (
          <div 
            key={comboId}
            className="stat-pill"
            style={{ backgroundColor: 'var(--pixel-accent)' }}
          >
            <span>{getComboEmoji(comboId)}</span>
            <span>{getComboName(comboId)}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
