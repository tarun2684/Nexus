import { Quest } from '../api'

interface QuestBoardProps {
  quests?: Record<string, Quest[]>
  onComplete: (questId: string) => void
  completedToday: string[]
}

export default function QuestBoard({ quests, onComplete, completedToday }: QuestBoardProps) {
  if (!quests || Object.keys(quests).length === 0) {
    return (
      <div className="card-pixel text-center">
        <p>No quests available yet.</p>
      </div>
    )
  }

  const getCategoryIcon = (category: string): string => {
    const icons: Record<string, string> = {
      fitness: '💪',
      learning: '📚',
      creativity: '🎨',
      social: '👥',
      mindfulness: '🧘',
      career: '💼',
      finance: '💰',
      habits: '🔄',
    }
    return icons[category] || '📋'
  }

  return (
    <div>
      {Object.entries(quests).map(([category, categoryQuests]) => (
        <div key={category} className="mb-2">
          <h3 
            className="flex items-center gap-1 mb-1"
            style={{ fontFamily: 'var(--font-mono)', fontSize: '1rem' }}
          >
            <span>{getCategoryIcon(category)}</span>
            <span>{category.charAt(0).toUpperCase() + category.slice(1)}</span>
          </h3>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1rem' }}>
            {categoryQuests.map((quest) => {
              const isCompleted = completedToday.includes(quest.id)
              
              return (
                <div 
                  key={quest.id}
                  className={`quest-card ${isCompleted ? 'completed' : ''}`}
                >
                  <div className="flex justify-between items-center">
                    <h4 style={{ fontWeight: 'bold' }}>{quest.title}</h4>
                    {isCompleted && <span style={{ color: 'var(--pixel-success)' }}>✅</span>}
                  </div>
                  
                  <div className="quest-reward">
                    <span>+{quest.xp} XP</span>
                    <span>•</span>
                    <span>+{quest.coins} coins</span>
                    {quest.stat_key && (
                      <>
                        <span>•</span>
                        <span>{quest.stat_key}</span>
                      </>
                    )}
                  </div>
                  
                  {!isCompleted && (
                    <button
                      className="btn-pixel success mt-2"
                      onClick={() => onComplete(quest.id)}
                      style={{ width: '100%' }}
                    >
                      Complete Quest
                    </button>
                  )}
                  
                  {isCompleted && (
                    <div 
                      className="mt-2 text-muted"
                      style={{ fontSize: '0.75rem', textAlign: 'center' }}
                    >
                      Completed today ✓
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      ))}
    </div>
  )
}
