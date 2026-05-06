import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { LCHF_TARGETS, calcMacroRatios } from '../utils/ketoCalculator'

const COLORS = {
  carbs: '#f59e0b',
  protein: '#3b82f6',
  fat: '#22c55e',
}

const LABELS = { carbs: '탄수화물', protein: '단백질', fat: '지방' }

export default function MacroChart({ carbs, protein, fat }) {
  const ratios = calcMacroRatios(carbs, protein, fat)
  const hasData = carbs + protein + fat > 0

  const actual = [
    { name: LABELS.carbs, value: ratios.carbs, color: COLORS.carbs },
    { name: LABELS.protein, value: ratios.protein, color: COLORS.protein },
    { name: LABELS.fat, value: ratios.fat, color: COLORS.fat },
  ]

  const target = [
    { name: LABELS.carbs, value: LCHF_TARGETS.carbs, color: COLORS.carbs },
    { name: LABELS.protein, value: LCHF_TARGETS.protein, color: COLORS.protein },
    { name: LABELS.fat, value: LCHF_TARGETS.fat, color: COLORS.fat },
  ]

  return (
    <div className="space-y-3">
      <div className="flex justify-between text-xs text-gray-500 px-1">
        <span className="font-semibold text-gray-700">오늘 섭취 비율</span>
        <span>목표: 탄 10% / 단 25% / 지 65%</span>
      </div>

      {hasData ? (
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie
              data={actual}
              cx="30%"
              cy="50%"
              outerRadius={70}
              dataKey="value"
              label={({ name, value }) => `${value}%`}
              labelLine={false}
            >
              {actual.map((entry) => (
                <Cell key={entry.name} fill={entry.color} />
              ))}
            </Pie>
            <Pie
              data={target}
              cx="72%"
              cy="50%"
              outerRadius={70}
              dataKey="value"
              label={({ value }) => `${value}%`}
              labelLine={false}
              opacity={0.45}
            >
              {target.map((entry) => (
                <Cell key={entry.name} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip formatter={(v) => `${v}%`} />
          </PieChart>
        </ResponsiveContainer>
      ) : (
        <div className="h-[200px] flex flex-col items-center justify-center text-gray-400 gap-2">
          <span className="text-4xl">🥑</span>
          <p className="text-sm">아직 기록된 식사가 없어요</p>
        </div>
      )}

      <div className="flex justify-around text-xs">
        <span className="text-gray-600 font-medium">현재</span>
        <span className="text-gray-400">목표</span>
      </div>

      {/* 범례 */}
      <div className="flex justify-center gap-4 text-xs">
        {Object.entries(LABELS).map(([key, label]) => (
          <span key={key} className="flex items-center gap-1">
            <span
              className="inline-block w-2.5 h-2.5 rounded-full"
              style={{ background: COLORS[key] }}
            />
            {label}
          </span>
        ))}
      </div>
    </div>
  )
}
