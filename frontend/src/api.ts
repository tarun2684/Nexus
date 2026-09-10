import axios from 'axios'

const API_BASE = '/api'

export interface Quest {
  id: string
  title: string
  xp: number
  coins: number
  stat_key: string | null
}

export interface UserState {
  user_id: string
  display_name: string
  avatar: string
  level: number
  total_xp: number
  coins: number
  trophies: number
  streak_count: number
  streak_longest: number
  last_active: string | null
  rank: number | null
  today_xp: number
  quests_done_today: string[]
  combos_fired_today: string[]
}

export interface CompleteQuestResponse {
  success: boolean
  xp_earned: number
  coins_earned: number
  new_total_xp: number
  old_level: number
  new_level: number
  leveled_up: boolean
  streak_count: number
  combo_multiplier: number
  achievements_unlocked: string[]
  message: string
}

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

export async function fetchQuests(): Promise<Record<string, Quest[]>> {
  const response = await api.get<Record<string, Quest[]>>('/quests')
  return response.data
}

export async function fetchUserState(): Promise<UserState> {
  const response = await api.get<UserState>('/me/state')
  return response.data
}

export async function completeQuest(questId: string): Promise<CompleteQuestResponse> {
  const response = await api.post<CompleteQuestResponse>(`/quests/${questId}/complete`, {})
  return response.data
}

export async function fetchHistory(days: number = 30) {
  const response = await api.get(`/me/history?days=${days}`)
  return response.data
}
