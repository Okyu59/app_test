import os
import base64
import json
from io import BytesIO

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import anthropic
from PIL import Image

load_dotenv()

app = FastAPI(title="KetoMate API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

LCHF_TARGETS = {"carbs": 0.10, "protein": 0.25, "fat": 0.65}

ANALYZE_PROMPT = """이 음식 사진을 분석해서 아래 JSON 형식으로만 응답해줘. 다른 텍스트는 절대 포함하지 마.

{
  "food_name": "음식 이름 (한국어)",
  "calories": 숫자(kcal),
  "carbs": 숫자(g),
  "protein": 숫자(g),
  "fat": 숫자(g)
}

- 사진에 여러 음식이 있으면 food_name을 쉼표로 나열하고 전체 합산 수치를 반환해.
- 음식이 없거나 판별 불가면 calories를 0으로 설정해.
- 모든 수치는 정수로 반환해."""


def calculate_keto_score(carbs_g: float, protein_g: float, fat_g: float) -> dict:
    carb_cal = carbs_g * 4
    protein_cal = protein_g * 4
    fat_cal = fat_g * 9
    total_cal = carb_cal + protein_cal + fat_cal

    if total_cal == 0:
        return {"score": 0, "coaching": "음식 데이터가 없습니다.", "ratios": {"carbs": 0, "protein": 0, "fat": 0}}

    actual = {
        "carbs": carb_cal / total_cal,
        "protein": protein_cal / total_cal,
        "fat": fat_cal / total_cal,
    }

    # 각 영양소 편차 계산 (목표 대비 절대 편차 비율 합산)
    deviations = {
        k: abs(actual[k] - LCHF_TARGETS[k]) / LCHF_TARGETS[k]
        for k in LCHF_TARGETS
    }
    avg_deviation = sum(deviations.values()) / 3
    score = max(0, round(10 * (1 - min(avg_deviation, 1)), 1))

    # 코칭 메시지 (가장 편차가 큰 영양소 기준)
    worst = max(deviations, key=deviations.get)
    coaching = _get_coaching(worst, actual[worst], LCHF_TARGETS[worst])

    return {
        "score": score,
        "coaching": coaching,
        "ratios": {k: round(v * 100, 1) for k, v in actual.items()},
    }


def _get_coaching(nutrient: str, actual_ratio: float, target_ratio: float) -> str:
    over = actual_ratio > target_ratio
    messages = {
        "carbs": (
            "탄수화물이 너무 많아요! 밥·빵·과일을 줄이고 지방을 늘려보세요.",
            "탄수화물이 목표보다 낮아요. LCHF는 탄 10%를 유지하면 돼요. 잘 하고 있어요!",
        ),
        "protein": (
            "단백질이 과해요. 지방 비율을 높이는 데 집중해보세요.",
            "단백질이 부족해요. 달걀·생선·닭가슴살을 추가해보세요.",
        ),
        "fat": (
            "지방이 목표를 초과했어요. 다른 영양소 균형을 확인해보세요.",
            "지방이 부족해요! 아보카도·올리브유·버터를 더 추가해보세요.",
        ),
    }
    return messages[nutrient][0] if over else messages[nutrient][1]


@app.post("/api/analyze-meal")
async def analyze_meal(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드 가능합니다.")

    raw = await file.read()

    # 이미지 리사이즈 (Claude API 제한 대응)
    img = Image.open(BytesIO(raw))
    img.thumbnail((1024, 1024), Image.LANCZOS)
    buf = BytesIO()
    fmt = "JPEG" if img.mode != "RGBA" else "PNG"
    img.convert("RGB" if fmt == "JPEG" else "RGBA").save(buf, format=fmt)
    image_data = base64.standard_b64encode(buf.getvalue()).decode("utf-8")
    media_type = f"image/{fmt.lower()}"

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {"type": "text", "text": ANALYZE_PROMPT},
                    ],
                }
            ],
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Claude API 오류: {str(e)}")

    raw_text = response.content[0].text.strip()

    # JSON 파싱
    try:
        # 코드블록 제거
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
        nutrition = json.loads(raw_text.strip())
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="영양 분석 결과를 파싱할 수 없습니다.")

    keto = calculate_keto_score(
        nutrition.get("carbs", 0),
        nutrition.get("protein", 0),
        nutrition.get("fat", 0),
    )

    return {
        "nutrition": nutrition,
        "keto_score": keto["score"],
        "coaching": keto["coaching"],
        "ratios": keto["ratios"],
    }


@app.get("/health")
def health():
    return {"status": "ok"}
