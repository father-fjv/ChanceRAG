#!/usr/bin/env python3
"""FAQ questions data."""

# FAQ에서 추출한 질문들
FAQ_QUESTIONS = [
    "단원이 중도 계약 해지를 했을 때, 종료평가를 입력해야 하나요?",
    "단원이 아파서 일시귀국을 희망하는데, 가능한가요?",
    "단원이 조부모의 사망으로 일시귀국을 실시하려 합니다. 최대 몇 월 몇 일까지 단원이 파견국에 복귀해야 하나요?",
    "단원이 일시귀국과 휴가를 함께 붙여서 실시하고 싶다고 합니다. 가능한가요?",
    "단원이 활동물품으로 에어컨을 구매하고 싶다고 합니다. 에어컨을 활동물품비로 구매할 수 있나요?",
    "2명의 단원이 1명 분의 숙박바우처만 사용해서 하나의 숙박시설을 함께 이용하고 싶다고 합니다. 가능한가요?",
    "단원이 3개월 계약 연장을 희망합니다. 현지 건강검진을 실시해야 하나요?",
    "단원이 1개월 이상 귀로여행을 실시할 수 있나요?",
    "활동 지역이 지방이고 임기 만료 후 한국으로 귀국하는 단원의 경우, 임지에서부터 공항까지 교통비 지원이 가능한가요?",
    "한국에서 국내 건강검진을 받지 못하는 경우, 단원에게 어떻게 안내해야 하나요?",
    "주거지 임차 시 부동산 수수료를 지원받을 수 있나요?",
    "주거지 임차 시 주거비로 보증금을 지출할 수 있나요?",
    "활동물품비로 에어컨 구매할 수 있나요?",
    "A 단원이 어머니 10일, 친구 10일씩 초청을 한다고 합니다. 가능한가요?",
    "단원이 복학을 위해 조기귀국을 신청한다고 합니다. 단원 경력 증명서에 활동 기간은 어떻게 기재되나요?"
]

def get_random_questions(count=4):
    """Get random questions from FAQ."""
    import random
    return random.sample(FAQ_QUESTIONS, min(count, len(FAQ_QUESTIONS)))

def get_all_questions():
    """Get all FAQ questions."""
    return FAQ_QUESTIONS.copy()

if __name__ == "__main__":
    print("FAQ 질문들:")
    for i, q in enumerate(FAQ_QUESTIONS, 1):
        print(f"{i:2d}. {q}")
    
    print(f"\n랜덤 4개 질문:")
    random_questions = get_random_questions(4)
    for i, q in enumerate(random_questions, 1):
        print(f"{i}. {q}")
