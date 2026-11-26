---
description: "/medi-gemini (/MEDI-GEMINI) — JEV Router × Clinical Deep Twin × 0-Dependency Ontology 기반 1인 대학병원 다학제 협진 & 7대 Med-Gemini 임상 진단·치료 방침 Assist 워크플로우"
---

# 🩺 `/medi-gemini` (`/MEDI-GEMINI`) — Medi-Gemini v7.0 Neurosymbolic Clinical Assist Workflow

사용자가 `/medi-gemini` 또는 `/MEDI-GEMINI` 를 호출하면 반드시 아래 절차를 실행합니다.

// turbo
1. 먼저 스킬 명세서 `c:\Users\USER\Desktop\luca연구에이전트\.agents\skills\ndb_medi_gemini_engine\SKILL.md` 를 준수하여, 사용자의 임상 질의·증례·약물·영상·EHR 내용을 `Medi-Gemini v7.0` 통합 오케스트레이터로 선제 실행합니다:
```powershell
python -X utf8 "c:\Users\USER\Desktop\luca연구에이전트\.agents\skills\ndb_medi_gemini_engine\ndb_medi_gemini_agent.py" --mode neurosymbolic --case "<사용자 증례 또는 임상 질의>"
```
2. 첨부 영상이 있으면 `--image "<경로>" --modality <xray|cxr|ecg|mri|ct>` 옵션을, 장문 의무기록이 있으면 `--ehr-file "<경로>"` 옵션을 함께 전달합니다.
3. 출력된 좌뇌 결정론적 결과(**17대 Red Flag·NEWS2 킬스위치, 찰리 멍거 3-바구니 `YES/NO/TOO TOUGH`, 2025~2026 다학제 협진 Delta, `eGFR`/CPIC `PGx` 약물 방화벽, Top-3 베이즈 감별진단 & `Must-Not-Miss`, SOAP/HIRA 2026 방어, 환자 안심 비유**)를 단 하나의 안전 경계도 누락 없이 정리해 보고합니다.
4. 사용자가 새로운 임상 지침이나 학회 최신 기준을 학습시키길 원하면 `learn_new_guideline_delta()` 로 SQLite 온톨로지 DB 및 `wiki/MOC_Medi_Gemini_Ontology.md` 에 영구 각인합니다.
5. 사용자가 웹 UI 실행을 원하면 `c:\Users\USER\Desktop\luca연구에이전트\.agents\skills\ndb_medi_gemini_engine\launch_medi_gemini_app.bat` (바탕화면 `Medi-Gemini 다학제협진` 아이콘)을 안내합니다.
