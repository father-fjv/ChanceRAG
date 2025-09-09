# ChanceRAG

사내 직원이 규정을 빠르게 찾아보고 이해할 수 있도록, PDF 규정을 RAG로 검색·답변해 주는 웹 기반 챗봇입니다.

## 🚀 주요 기능

- **🔍 지능형 검색**: FAISS 벡터 데이터베이스를 활용한 의미적 문서 검색
- **🤖 AI 답변 생성**: OpenAI GPT-4를 활용한 이해하기 쉬운 답변 생성
- **🇰🇷 한국어 최적화**: 커스텀 한국어 토크나이저를 활용한 한국어 텍스트 처리
- **⚡ 실시간 스트리밍**: 답변을 실시간으로 스트리밍하여 빠른 응답 속도
- **📄 PDF 문서 처리**: Synapsoft DocuAnalyzer를 활용한 고품질 PDF 텍스트 추출
- **🔗 출처 인용**: 답변에 사용된 문서의 정확한 출처 표시

## 🛠️ 기술 스택

- **Backend**: Python 3.10+, FastAPI, Uvicorn
- **RAG Framework**: LangChain
- **LLM**: OpenAI GPT-4, GPT-4o
- **Vector Database**: FAISS
- **Document Processing**: PyPDF, Custom Korean Tokenizer
- **Embeddings**: OpenAI Embeddings, Sentence-Transformers

## 📦 설치 및 실행

### 요구사항

- Python 3.10+
- OpenAI API Key

### 설치

```bash
# 저장소 클론
git clone https://github.com/father-fjv/ChanceRAG.git
cd ChanceRAG

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 환경 설정

```bash
# 환경 변수 파일 복사
cp env.example .env

# .env 파일에서 OpenAI API 키 설정
# OPENAI_API_KEY=your_openai_api_key_here
```

### 실행

```bash
# 개발 서버 실행
python run.py

# 또는 직접 실행
python -m src.chancerag.main
```

서버가 실행되면 http://localhost:8000 에서 웹 인터페이스에 접근할 수 있습니다.

## 📁 프로젝트 구조

```
ChanceRAG/
├── src/
│   └── chancerag/
│       ├── core/                    # 핵심 RAG 로직
│       │   ├── document_processor.py
│       │   ├── vector_store.py
│       │   ├── retriever.py
│       │   └── generator.py
│       ├── models/                  # 데이터 모델
│       │   ├── document.py
│       │   ├── query.py
│       │   └── response.py
│       ├── api/                     # API 엔드포인트
│       │   ├── routes.py
│       │   └── dependencies.py
│       ├── config/                  # 설정 관리
│       │   └── settings.py
│       └── main.py                  # 메인 애플리케이션
├── tests/                           # 테스트 코드
├── data/                            # 데이터 파일
├── docs/                            # 문서
├── scripts/                         # 스크립트
├── requirements.txt
├── pyproject.toml
├── run.py
└── README.md
```

## 🔧 API 사용법

### 문서 업로드

```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_document.pdf"
```

### 질문하기

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "출장비 정산 한도는 얼마인가요?",
    "top_k": 5,
    "score_threshold": 0.7
  }'
```

### 스트리밍 답변

```bash
curl -X POST "http://localhost:8000/api/v1/query/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "휴가 신청 절차는 어떻게 되나요?",
    "streaming": true
  }'
```

## 🧪 테스트

```bash
# 테스트 실행
pytest tests/

# 특정 테스트 실행
pytest tests/test_rag_system.py -v
```

## 📊 시스템 상태 확인

```bash
# 시스템 통계 확인
curl http://localhost:8000/api/v1/stats

# 헬스 체크
curl http://localhost:8000/api/v1/health
```

## 🔍 API 문서

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🚀 배포

### Docker를 사용한 배포

```bash
# Docker 이미지 빌드
docker build -t chancerag .

# 컨테이너 실행
docker run -p 8000:8000 --env-file .env chancerag
```

### 프로덕션 환경

```bash
# Gunicorn으로 실행
gunicorn src.chancerag.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 연락처

프로젝트 링크: [https://github.com/father-fjv/ChanceRAG](https://github.com/father-fjv/ChanceRAG)

## 🙏 감사의 말

이 프로젝트는 [langchain-teddynote](https://github.com/teddylee777/langchain-teddynote) 패키지의 구현 패턴을 참조하여 직접 구현되었습니다.