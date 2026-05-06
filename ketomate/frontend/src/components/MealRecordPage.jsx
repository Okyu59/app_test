import { useState, useRef } from 'react'
import { getScoreColor, getScoreBg } from '../utils/ketoCalculator'

export default function MealRecordPage({ onBack, onSave }) {
  const [preview, setPreview] = useState(null)
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const inputRef = useRef()

  function handleFile(f) {
    if (!f) return
    setFile(f)
    setPreview(URL.createObjectURL(f))
    setResult(null)
    setError(null)
  }

  function onInputChange(e) {
    handleFile(e.target.files[0])
  }

  function onDrop(e) {
    e.preventDefault()
    handleFile(e.dataTransfer.files[0])
  }

  async function analyze() {
    if (!file) return
    setLoading(true)
    setError(null)
    try {
      const fd = new FormData()
      fd.append('file', file)
      const res = await fetch('/api/analyze-meal', { method: 'POST', body: fd })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || '분석 실패')
      }
      const data = await res.json()
      setResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  function save() {
    if (!result) return
    onSave({
      food_name: result.nutrition.food_name,
      calories: result.nutrition.calories,
      carbs: result.nutrition.carbs,
      protein: result.nutrition.protein,
      fat: result.nutrition.fat,
      keto_score: result.keto_score,
      coaching: result.coaching,
    })
    onBack()
  }

  return (
    <div className="min-h-screen bg-keto-bg flex flex-col">
      {/* 헤더 */}
      <header className="flex items-center gap-3 px-4 pt-12 pb-4 bg-white shadow-sm">
        <button
          onClick={onBack}
          className="w-9 h-9 flex items-center justify-center rounded-full bg-gray-100 text-gray-600 hover:bg-gray-200 transition"
        >
          ←
        </button>
        <h1 className="text-lg font-bold text-gray-800">식사 기록하기</h1>
      </header>

      <div className="flex-1 overflow-y-auto px-4 py-5 space-y-4">
        {/* 이미지 업로드 영역 */}
        <div
          className="rounded-2xl border-2 border-dashed border-gray-300 bg-white flex flex-col items-center justify-center gap-3 p-6 cursor-pointer hover:border-green-400 transition"
          onClick={() => inputRef.current?.click()}
          onDrop={onDrop}
          onDragOver={(e) => e.preventDefault()}
        >
          {preview ? (
            <img
              src={preview}
              alt="음식 미리보기"
              className="w-full max-h-56 object-cover rounded-xl"
            />
          ) : (
            <>
              <span className="text-5xl">📸</span>
              <p className="text-sm font-medium text-gray-600">음식 사진을 올려주세요</p>
              <p className="text-xs text-gray-400">탭하거나 파일을 드래그하세요</p>
            </>
          )}
          <input
            ref={inputRef}
            type="file"
            accept="image/*"
            capture="environment"
            className="hidden"
            onChange={onInputChange}
          />
        </div>

        {preview && !result && (
          <button
            onClick={analyze}
            disabled={loading}
            className="w-full py-3.5 rounded-2xl bg-gradient-to-r from-green-500 to-teal-500 text-white font-bold text-base shadow-md active:scale-95 transition disabled:opacity-60"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin w-5 h-5" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                </svg>
                AI 분석 중...
              </span>
            ) : '🔍 영양 분석하기'}
          </button>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-2xl px-4 py-3 text-sm text-red-600">
            ⚠️ {error}
          </div>
        )}

        {/* 분석 결과 */}
        {result && (
          <div className="space-y-3 animate-fadeIn">
            {/* 음식명 + 칼로리 */}
            <div className="bg-white rounded-2xl p-4 shadow-sm">
              <h2 className="font-bold text-gray-800 text-base">{result.nutrition.food_name}</h2>
              <p className="text-3xl font-extrabold text-green-500 mt-1">
                {result.nutrition.calories} <span className="text-base font-medium text-gray-400">kcal</span>
              </p>
            </div>

            {/* 탄단지 */}
            <div className="grid grid-cols-3 gap-2">
              <MacroTile label="탄수화물" value={result.nutrition.carbs} color="bg-yellow-50 text-yellow-600" />
              <MacroTile label="단백질" value={result.nutrition.protein} color="bg-blue-50 text-blue-600" />
              <MacroTile label="지방" value={result.nutrition.fat} color="bg-green-50 text-green-600" />
            </div>

            {/* 케토 점수 */}
            <div className={`rounded-2xl p-4 border ${getScoreBg(result.keto_score)}`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-gray-500 font-medium">LCHF 점수</p>
                  <p className={`text-4xl font-extrabold ${getScoreColor(result.keto_score)}`}>
                    {result.keto_score}
                    <span className="text-base font-medium text-gray-400"> / 10</span>
                  </p>
                </div>
                <ScoreEmoji score={result.keto_score} />
              </div>
              <p className="text-sm text-gray-600 mt-2 leading-relaxed">💬 {result.coaching}</p>
            </div>

            {/* 비율 */}
            <div className="bg-white rounded-2xl p-4 shadow-sm space-y-2">
              <p className="text-xs font-semibold text-gray-500 mb-2">이 식사의 탄단지 비율</p>
              <RatioRow label="탄수화물" actual={result.ratios.carbs} target={10} color="#f59e0b" />
              <RatioRow label="단백질" actual={result.ratios.protein} target={25} color="#3b82f6" />
              <RatioRow label="지방" actual={result.ratios.fat} target={65} color="#22c55e" />
            </div>

            <button
              onClick={save}
              className="w-full py-3.5 rounded-2xl bg-gradient-to-r from-green-500 to-teal-500 text-white font-bold text-base shadow-md active:scale-95 transition"
            >
              ✅ 오늘 식단에 추가하기
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

function MacroTile({ label, value, color }) {
  return (
    <div className={`rounded-2xl p-3 text-center ${color} bg-opacity-50`}>
      <p className="text-lg font-extrabold">{value}g</p>
      <p className="text-xs font-medium opacity-70 mt-0.5">{label}</p>
    </div>
  )
}

function RatioRow({ label, actual, target, color }) {
  const pct = Math.min(actual, 100)
  const targetPct = Math.min(target, 100)
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-gray-600">{label}</span>
        <span className="font-medium" style={{ color }}>
          {actual}% <span className="text-gray-300">/ 목표 {target}%</span>
        </span>
      </div>
      <div className="relative h-2 bg-gray-100 rounded-full overflow-visible">
        <div
          className="h-full rounded-full"
          style={{ width: `${pct}%`, background: color }}
        />
        {/* 목표 마커 */}
        <div
          className="absolute top-1/2 -translate-y-1/2 w-0.5 h-4 bg-gray-400 rounded"
          style={{ left: `${targetPct}%` }}
        />
      </div>
    </div>
  )
}

function ScoreEmoji({ score }) {
  if (score >= 8) return <span className="text-4xl">🎉</span>
  if (score >= 5) return <span className="text-4xl">👍</span>
  return <span className="text-4xl">💪</span>
}
