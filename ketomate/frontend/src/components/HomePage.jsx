import MacroChart from './MacroChart'
import MealCard from './MealCard'
import NutrientBar from './NutrientBar'
import { calcMacroRatios, getScoreColor } from '../utils/ketoCalculator'

const DAILY_TARGETS = { carbs: 50, protein: 125, fat: 144 }

export default function HomePage({ daily, onRecord, onReset }) {
  const ratios = calcMacroRatios(daily.carbs, daily.protein, daily.fat)
  const avgScore =
    daily.meals.length > 0
      ? (daily.meals.reduce((s, m) => s + m.keto_score, 0) / daily.meals.length).toFixed(1)
      : null

  const today = new Date().toLocaleDateString('ko-KR', {
    month: 'long',
    day: 'numeric',
    weekday: 'short',
  })

  return (
    <div className="min-h-screen bg-keto-bg flex flex-col">
      {/* 헤더 */}
      <header className="px-4 pt-12 pb-5 bg-gradient-to-br from-green-500 to-teal-500 text-white">
        <p className="text-sm opacity-80">{today}</p>
        <h1 className="text-2xl font-extrabold mt-1 tracking-tight">🥑 KetoMate</h1>
        <p className="text-xs opacity-75 mt-0.5">저탄고지(LCHF) 식단 트래커</p>

        {avgScore !== null && (
          <div className="mt-3 inline-flex items-center gap-2 bg-white/20 rounded-2xl px-4 py-2">
            <span className="text-xs opacity-90">오늘 평균 점수</span>
            <span className="text-xl font-extrabold">{avgScore}/10</span>
          </div>
        )}
      </header>

      <div className="flex-1 overflow-y-auto px-4 py-5 space-y-4 pb-28">
        {/* 오늘 누적 요약 카드 */}
        <div className="bg-white rounded-2xl p-4 shadow-sm">
          <div className="flex justify-between items-center mb-3">
            <h2 className="font-bold text-gray-800">오늘 누적 섭취량</h2>
            <span className="text-2xl font-extrabold text-green-500">
              {Math.round(daily.calories)}
              <span className="text-sm font-medium text-gray-400"> kcal</span>
            </span>
          </div>
          <div className="space-y-2.5">
            <NutrientBar
              label="탄수화물"
              value={daily.carbs}
              target={DAILY_TARGETS.carbs}
              color="#f59e0b"
            />
            <NutrientBar
              label="단백질"
              value={daily.protein}
              target={DAILY_TARGETS.protein}
              color="#3b82f6"
            />
            <NutrientBar
              label="지방"
              value={daily.fat}
              target={DAILY_TARGETS.fat}
              color="#22c55e"
            />
          </div>
        </div>

        {/* 탄단지 비율 차트 */}
        <div className="bg-white rounded-2xl p-4 shadow-sm">
          <MacroChart carbs={daily.carbs} protein={daily.protein} fat={daily.fat} />
        </div>

        {/* 오늘 식사 목록 */}
        {daily.meals.length > 0 && (
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <h2 className="font-bold text-gray-800">오늘 식사 ({daily.meals.length}끼)</h2>
              <button
                onClick={onReset}
                className="text-xs text-red-400 hover:text-red-600 transition"
              >
                초기화
              </button>
            </div>
            {[...daily.meals].reverse().map((meal, i) => (
              <MealCard key={meal.timestamp} meal={meal} index={i} />
            ))}
          </div>
        )}
      </div>

      {/* 하단 고정 버튼 */}
      <div className="fixed bottom-0 left-0 right-0 px-4 py-4 bg-keto-bg border-t border-gray-100 safe-pb">
        <button
          onClick={onRecord}
          className="w-full py-4 rounded-2xl bg-gradient-to-r from-green-500 to-teal-500 text-white font-bold text-lg shadow-lg active:scale-95 transition flex items-center justify-center gap-2"
        >
          <span>📸</span>
          <span>식사 기록하기</span>
        </button>
      </div>
    </div>
  )
}
