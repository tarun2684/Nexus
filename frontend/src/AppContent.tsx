import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { fetchQuests, fetchUserState, completeQuest, type Quest } from './api'
import HUD from './components/HUD'
import CharacterPanel from './components/CharacterPanel'
import QuestBoard from './components/QuestBoard'
import Toast from './components/Toast'

function AppContent() {
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null)
  const queryClient = useQueryClient()

  const { data: userState, isLoading: loadingUser } = useQuery({
    queryKey: ['userState'],
    queryFn: fetchUserState,
  })

  const { data: quests, isLoading: loadingQuests } = useQuery({
    queryKey: ['quests'],
    queryFn: fetchQuests,
  })

  const completeMutation = useMutation({
    mutationFn: (questId: string) => completeQuest(questId),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['userState'] })
      queryClient.invalidateQueries({ queryKey: ['quests'] })
      setToast({ message: data.message, type: 'success' })
      setTimeout(() => setToast(null), 3000)
    },
    onError: (error: Error) => {
      setToast({ message: error.message, type: 'error' })
      setTimeout(() => setToast(null), 3000)
    },
  })

  if (loadingUser || loadingQuests) {
    return (
      <div className="flex items-center justify-center" style={{ minHeight: '100vh' }}>
        <div className="loading-spinner"></div>
      </div>
    )
  }

  return (
    <div>
      <HUD userState={userState} />
      
      <main style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
        <CharacterPanel userState={userState} />
        
        <section style={{ marginTop: '2rem' }}>
          <h2 style={{ marginBottom: '1rem' }}>Quest Board</h2>
          <QuestBoard 
            quests={quests} 
            onComplete={(questId) => completeMutation.mutate(questId)}
            completedToday={userState?.quests_done_today || []}
          />
        </section>
      </main>

      {toast && <Toast message={toast.message} type={toast.type} />}
    </div>
  )
}

export default AppContent
