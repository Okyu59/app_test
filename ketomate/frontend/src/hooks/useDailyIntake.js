import { useState, useCallback } from 'react'
import { todayKey } from '../utils/ketoCalculator'

const STORAGE_KEY = 'ketomate_daily'

function loadToday() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return emptyDay()
    const all = JSON.parse(raw)
    return all[todayKey()] ?? emptyDay()
  } catch {
    return emptyDay()
  }
}

function emptyDay() {
  return { calories: 0, carbs: 0, protein: 0, fat: 0, meals: [] }
}

function saveToday(day) {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    const all = raw ? JSON.parse(raw) : {}
    all[todayKey()] = day
    // 7일치만 보관
    const keys = Object.keys(all).sort().slice(-7)
    const trimmed = {}
    keys.forEach((k) => (trimmed[k] = all[k]))
    localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed))
  } catch {}
}

export function useDailyIntake() {
  const [daily, setDaily] = useState(loadToday)

  const addMeal = useCallback((meal) => {
    setDaily((prev) => {
      const next = {
        calories: prev.calories + meal.calories,
        carbs: prev.carbs + meal.carbs,
        protein: prev.protein + meal.protein,
        fat: prev.fat + meal.fat,
        meals: [
          ...prev.meals,
          { ...meal, timestamp: new Date().toISOString() },
        ],
      }
      saveToday(next)
      return next
    })
  }, [])

  const resetDay = useCallback(() => {
    const empty = emptyDay()
    setDaily(empty)
    saveToday(empty)
  }, [])

  return { daily, addMeal, resetDay }
}
