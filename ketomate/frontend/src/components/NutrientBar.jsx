const TARGETS = { carbs: 50, protein: 125, fat: 144 } // 기준: 2000kcal LCHF

export default function NutrientBar({ label, value, target, color, unit = 'g' }) {
  const pct = Math.min(Math.round((value / target) * 100), 100)

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-gray-600 font-medium">{label}</span>
        <span className="text-gray-500">
          {value.toFixed(1)}{unit} / {target}{unit}
        </span>
      </div>
      <div className="h-2.5 rounded-full bg-gray-100 overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${pct}%`, background: color }}
        />
      </div>
    </div>
  )
}
