import { useState } from 'react'
import HomePage from './components/HomePage'
import MealRecordPage from './components/MealRecordPage'
import { useDailyIntake } from './hooks/useDailyIntake'

export default function App() {
  const [page, setPage] = useState('home')
  const { daily, addMeal, resetDay } = useDailyIntake()

  return (
    <div className="max-w-md mx-auto relative">
      {page === 'home' && (
        <HomePage
          daily={daily}
          onRecord={() => setPage('record')}
          onReset={resetDay}
        />
      )}
      {page === 'record' && (
        <MealRecordPage
          onBack={() => setPage('home')}
          onSave={addMeal}
        />
      )}
    </div>
  )
}
