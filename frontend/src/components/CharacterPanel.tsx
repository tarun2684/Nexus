import { UserState } from '../api'

interface CharacterPanelProps {
  userState?: UserState
}

export default function CharacterPanel({ userState }: CharacterPanelProps) {
  if (!userState) return null

  const getTitle = (level: number): string => {
    if (level >= 100) return 'Legend'
    if (level >= 75) return 'Grandmaster'
    if (level >= 50) return 'Master'
    if (level >= 30) return 'Expert'
    if (level >= 20) return 'Artisan'
    if (level >= 10) return 'Journeyman'
    if (level >= 5) return 'Apprentice'
    return 'Novice'
  }

  return (
    <div className="card-pixel character-panel">
      <div className="avatar-placeholder">
        {userState.avatar ? (
          <img 
            src={userState.avatar} 
            alt={userState.display_name}
            style={{ width: '100%', height: '100%', borderRadius: 'var(--radius-md)' }}
          />
        ) : (
          '🧙'
        )}
      </div>

      <div>
        <h2 style={{ marginBottom: 'var(--space-sm)' }}>
          {userState.display_name}
        </h2>
        <p className="text-muted" style={{ fontFamily: 'var(--font-mono)', fontSize: '0.875rem' }}>
          {getTitle(userState.level)}
        </p>

        <div className="flex gap-2 mt-2">
          <div className="stat-pill">
            <span>⭐ Total XP:</span>
            <span>{userState.total_xp.toLocaleString()}</span>
          </div>
          
          <div className="stat-pill">
            <span>📅 Today's XP:</span>
            <span>{userState.today_xp}</span>
          </div>
          
          <div className="stat-pill">
            <span>✅ Quests today:</span>
            <span>{userState.quests_done_today.length}</span>
          </div>
        </div>

        {userState.last_active && (
          <p className="text-muted mt-2" style={{ fontSize: '0.75rem' }}>
            Last active: {new Date(userState.last_active).toLocaleDateString()}
          </p>
        )}
      </div>
    </div>
  )
}
