# 🩺 NDB-HUMANOID MEDI-GEMINI AGENT 명세서
### (Medi-Gemini Antigravity Core ✕ Telegram Chat ✕ Humanoid Neurosymbolic Model)

> **대표님 비전 지정 (Director Sun-Jong Choi, M.D.)**  
> 본 에이전트는 의료 특화 **Google Med-Gemini 지능**과 **최선종 3×3 통증 기전 매트릭스**, **자체 SQLite DB(medi_gemini_neurosymbolic.db)** 및 **NDB 휴머노이드 행동 트리**가 유기 결합된 최첨단 융합 메디컬 에이전트 시스템입니다.

---

## 🎯 핵심 목적 (Core Purpose)
1. **의료 특화 MEDI-GEMINI ANTIGRAVITY 연구 & 작업**:
   - 안티그라비티 IDE 환경에서 척추외과/미세침습(BESS), 통증의학, PACS X-ray/MRI 판독, 요양급여 삭감 방지 연구 및 대시보드 자동 렌더링.
2. **텔레그램(Telegram) 실시간 의학 CHAT**:
   - 텔레그램 봇을 통해 대표님 및 의료진과 실시간 의학 질의응답, 3×3 통증 분석, 수액/약물 처방 추천, 휴머노이드 로봇 가동 상태 챗 수행.
3. **자체 DB + MEDI-GEMINI NEUROSYMBOLIC MODEL**:
   - **좌뇌**: 0-Dependency SQLite 팩트 DB (`medi_gemini_neurosymbolic.db`) ✖️ **우뇌**: Google Med-Gemini LLM 비동기 추론엔진의 변증법적 융합.

---

## 📐 3×3 통증 기전 매트릭스 신경학적 구조 (Choi Matrix)

| 생리 3축 \ 해부 3층위 | **1. 말초 / DRG 관문** | **2. 척수 후각** | **3. 중추 / 대뇌 (DMN)** |
| :--- | :--- | :--- | :--- |
| **A. 흥분성** *(Excitation)* | $Na_V1.7, Na_V1.3$ 이소성 자발발화 | 시냅스전 $Ca_V lpha_2\delta-1$ 활성 ➔ Glutamate 과다 | Thalamocortical 피질 과흥분 |
| **B. 억제성** *(Inhibition)* | SGC 교세포 GABA 토닉 억제 약화 | $KCC2$ 하향조절 ➔ GABA 탈억제 (**Disinhibition**) | PAG-RVM 하행 억제계 진통 붕괴 |
| **C. 전달성** *(Transmission)* | A-δ/C 섬유 전도 & HCN($I_h$) 진동 | Spinothalamic 2차 투사 & 시냅스 장기강화(LTP) | 시상 ➔ mPFC, Insula, DMN 통증 자아화 |

---

## 📱 텔레그램 챗봇 명령어 인터페이스 (Telegram Bot Commands)
- `/start` : NDB Medi-Gemini Agent 챗봇 가동 및 인사
- `/pain3x3 <증상>` : 최선종 3×3 통증 기전 매트릭스 9개 셀 자동 매핑
- `/medical <질의>` : Med-Gemini 지능 기반 정밀 의학 답변
- `/humanoid <액션코드>` : NDB 휴머노이드 로봇 의료 행동 및 액추에이터 제어 스캔
- `/iv_fluid <증상>` : NDB-IV #01~#30 영양수액 믹스 자동 추천

---

## 📂 폴더 구조 안내
- `database/medi_gemini_neurosymbolic.db` : 0-Dependency 자체 팩트 DB
- `agent_core/medi_gemini_core.py` : Med-Gemini 뉴로심볼릭 핵심 추론 엔진
- `telegram_bot/medi_gemini_telegram_bot.py` : 텔레그램 CHAT 연동 봇
- `dashboards/` : 3×3 통증 대시보드 및 의학 콘솔 HTML 3종
