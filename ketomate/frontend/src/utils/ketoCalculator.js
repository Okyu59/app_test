export const LCHF_TARGETS = { carbs: 10, protein: 25, fat: 65 }

export function calcCaloriesFromMacros(carbs, protein, fat) {
  return carbs * 4 + protein * 4 + fat * 9
}

export function calcMacroRatios(carbs, protein, fat) {
  const carbCal = carbs * 4
  const proteinCal = protein * 4
  const fatCal = fat * 9
  const total = carbCal + proteinCal + fatCal
  if (total === 0) return { carbs: 0, protein: 0, fat: 0 }
  return {
    carbs: Math.round((carbCal / total) * 100),
    protein: Math.round((proteinCal / total) * 100),
    fat: Math.round((fatCal / total) * 100),
  }
}

export function calcKetoScore(carbs, protein, fat) {
  const ratios = calcMacroRatios(carbs, protein, fat)
  const targets = LCHF_TARGETS
  const deviations = {
    carbs: Math.abs(ratios.carbs - targets.carbs) / targets.carbs,
    protein: Math.abs(ratios.protein - targets.protein) / targets.protein,
    fat: Math.abs(ratios.fat - targets.fat) / targets.fat,
  }
  const avg = (deviations.carbs + deviations.protein + deviations.fat) / 3
  return Math.max(0, Math.round(10 * (1 - Math.min(avg, 1)) * 10) / 10)
}

export function getScoreColor(score) {
  if (score >= 8) return 'text-green-500'
  if (score >= 5) return 'text-amber-500'
  return 'text-red-500'
}

export function getScoreBg(score) {
  if (score >= 8) return 'bg-green-50 border-green-200'
  if (score >= 5) return 'bg-amber-50 border-amber-200'
  return 'bg-red-50 border-red-200'
}

export function todayKey() {
  return new Date().toISOString().slice(0, 10)
}
