import { getScoreColor, getScoreBg } from '../utils/ketoCalculator'

export default function MealCard({ meal, index }) {
  const time = new Date(meal.timestamp).toLocaleTimeString('ko-KR', {
    hour: '2-digit',
    minute: '2-digit',
  })

  return (
    <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 space-y-2">
      <div className="flex justify-between items-start">
        <div>
          <p className="font-semibold text-gray-800 text-sm leading-tight">{meal.food_name}</p>
          <p className="text-xs text-gray-400 mt-0.5">{time}</p>
        </div>
        <div className={`text-center px-3 py-1 rounded-xl border text-xs font-bold ${getScoreBg(meal.keto_score)}`}>
          <span className={getScoreColor(meal.keto_score)}>{meal.keto_score}</span>
          <span className="text-gray-400">/10</span>
        </div>
      </div>

      <div className="flex gap-3 text-xs text-center">
        <div className="flex-1 bg-amber-50 rounded-xl py-1.5">
          <p className="text-amber-600 font-bold">{meal.calories}</p>
          <p className="text-gray-400">kcal</p>
        </div>
        <div className="flex-1 bg-yellow-50 rounded-xl py-1.5">
          <p className="text-yellow-600 font-bold">{meal.carbs}g</p>
          <p className="text-gray-400">탄</p>
        </div>
        <div className="flex-1 bg-blue-50 rounded-xl py-1.5">
          <p className="text-blue-600 font-bold">{meal.protein}g</p>
          <p className="text-gray-400">단</p>
        </div>
        <div className="flex-1 bg-green-50 rounded-xl py-1.5">
          <p className="text-green-600 font-bold">{meal.fat}g</p>
          <p className="text-gray-400">지</p>
        </div>
      </div>

      <p className="text-xs text-gray-500 bg-gray-50 rounded-xl px-3 py-2 leading-relaxed">
        💬 {meal.coaching}
      </p>
    </div>
  )
}
