import { UserState } from '../api'

interface HUDProps {
  userState?: UserState
}

export default function HUD({ userState }: HUDProps) {
  if (!userState) return null

  const xpForNextLevel = userState.level * 100 * Math.pow(1.5, userState.level - 1)
  const xpInCurrentLevel = userState.total_xp % xpForNextLevel
  const progressPercent = Math.min((xpInCurrentLevel / xpForNextLevel) * 100, 100)

  return (
    <header className="hud-bar">
      <div className="flex items-center gap-2">
        <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 'bold' }}>
          NEXUS
        </span>
      </div>

      <div className="flex items-center gap-2" style={{ marginLeft: 'auto' }}>
        <div className="stat-pill">
          <span>⭐</span>
          <span>Lv.{userState.level}</span>
        </div>
        
        <div className="stat-pill">
          <span>💰</span>
          <span>{userState.coins}</span>
        </div>
        
        <div className="stat-pill">
          <span>🔥</span>
          <span>{userState.streak_count}</span>
        </div>
        
        <div className="stat-pill">
          <span>🏆</span>
          <span>{userState.trophies}</span>
        </div>
      </div>

      <div style={{ width: '200px', marginLeft: 'var(--space-md)' }}>
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${progressPercent}%` }}
          />
        </div>
        <div style={{ fontSize: '0.625rem', textAlign: 'center', marginTop: '2px' }}>
          XP to next level
        </div>
      </div>
    </header>
  )
}
