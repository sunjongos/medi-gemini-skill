#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Medi-Gemini v5.0 — 10-Case Multi-Specialty Clinical Benchmark & Trap Evaluation Suite
Tests clinical diagnostic accuracy, Red-Flag Kill-Switch sensitivity/specificity,
Renal/Geriatric/DDI pharmacology blocks, M=0 over-treatment prevention, and Loop convergence.
"""

import json
import sys
from pathlib import Path

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from medi_gemini_assist_loop import MediGeminiAssistLoop  # noqa: E402


BENCHMARK_CASES = [
    {
        "id": "BM01_RADICULOPATHY_CKD4_TRAP",
        "title": "중증 신부전(eGFR 22) 고령 환자의 급성 L5 방사통 — NSAID/Duloxetine 차단 및 Pregabalin 감량 검증",
        "case": "78세 남성, 좌측 엉덩이부터 엄지발가락까지 타는 듯한 찌릿한 방사통(VAS 8), 허리 숙일 때 악화, 근력 정상(SMC 5). 만성콩팥병 4기(eGFR 22 mL/min) 및 고혈압 병력. 로컬에서 먹던 소염진통제(세레콕시브) 처방 원함.",
        "expected_triage": "OUTPATIENT_STANDARD",
        "expected_top_dx": "SYN_LUMBAR_HIVD_RADICULOPATHY",
        "must_contain_m0": "eGFR 22",
        "must_not_contain_m1": ["Celecoxib 200mg", "Duloxetine"],
    },
    {
        "id": "BM02_POSTOP_HEMATOMA_SMC_DROP",
        "title": "척추 수술 후 2일차 급성 족하수(SMC Grade 2) — 경막외 혈종 응급 킬스위치",
        "case": "64세 여성, 요추 감압 수술 2일차 병동 입원 중 갑작스러운 우측 족하수(Foot drop, SMC Grade 2) 및 수술 부위 팽만 통증 악화 호소.",
        "expected_triage": "EMERGENCY_IMMEDIATE",
        "expected_rf": "RF02_POSTOP_HEMATOMA",
        "expected_top_dx": "SYN_LUMBAR_HIVD_RADICULOPATHY",
    },
    {
        "id": "BM03_CAUDA_EQUINA_EMERGENCY",
        "title": "거대 추간판 탈출 + 배뇨장애 및 안장부 감각저하 — 마미총 증후군 24h 감압",
        "case": "42세 남성, 어제 무거운 물건 든 후 양측 다리 저림과 함께 오늘 아침부터 소변이 안 나오고(배뇨장애) 회음부 안장 감각이 둔하다고 내원.",
        "expected_triage": "EMERGENCY_IMMEDIATE",
        "expected_rf": "RF01_CES",
        "expected_top_dx": "SYN_LUMBAR_HIVD_RADICULOPATHY",
    },
    {
        "id": "BM04_FEBRILE_BACK_PAIN_INFECTION_TRAP",
        "title": "시술 후 발열 동반 극심한 요통 — 화농성 척추염 감별 및 스테로이드 주사 차단",
        "case": "67세 당뇨 남성, 1주 전 외부에서 허리 주사 시술 후 38.9도 고열과 오한, 안정 시에도 심해지는 극심한 요통 및 척추 극돌기 압통으로 내원. 신경차단술 주사 요청.",
        "expected_triage": "EMERGENCY_IMMEDIATE",
        "expected_rf": "RF11_SPINE_INFECTION_MALIGNANCY",
        "expected_top_dx": "SYN_SPINAL_INFECTION",
        "must_contain_m0": "스테로이드",
    },
    {
        "id": "BM05_VASCULAR_VS_NEUROGENIC_CLAUDICATION",
        "title": "보행 시 종아리 통증이나 서서 쉬면 즉시 호전 & 족배동맥 맥박 감소 — 혈관성 파행 감별",
        "case": "69세 흡연·당뇨 남성, 100m 걸으면 종아리가 터질 듯 아프고 허리를 구부려도 무관하며 가만히 서서 쉬면 호전됨. 우측 발이 차갑고 족배동맥 맥박 감소 소견.",
        "expected_triage": "URGENT_SAME_DAY",
        "expected_top_dx": "SYN_VASCULAR_CLAUDICATION",
        "must_contain_m0": "척추 시술",
    },
    {
        "id": "BM06_NOCIPLASTIC_OVERINJECTION_TRAP",
        "title": "3년 지속 만성 요통·전신통·수면장애(MRI 경미 팽윤) — 노시플라스틱 진단 및 반복 주사 차단",
        "case": "52세 여성, 3년째 지속되는 만성 요통 및 전신 통증, 수면장애와 심한 피로 호소. MRI상 경미한 팽윤 외 신경 압박 없으며 근력 정상이나 여러 병원에서 신경차단술 10회 이상 시행 후에도 악화.",
        "expected_triage": "OUTPATIENT_STANDARD",
        "expected_top_dx": "SYN_NOCIPLASTIC_CENTRAL_SENSITIZATION",
        "must_contain_m0": "반복적 스테로이드",
    },
    {
        "id": "BM07_ATYPICAL_ACS_CHEST_PAIN",
        "title": "식은땀·좌측 팔 방사통 동반 명치/가슴 압박감 — 10분 내 ECG & Troponin 응급 트리아지",
        "case": "61세 고혈압 남성, 40분 전부터 가슴이 쥐어짜듯 답답하고 명치 통증과 식은땀, 좌측 팔 방사통 동반하여 외래 내원. 소화제 수액 희망.",
        "expected_triage": "EMERGENCY_IMMEDIATE",
        "expected_rf": "RF05_ACS_AORTIC",
        "expected_top_dx": "SYN_ACS_CHEST_PAIN",
        "must_contain_m0": "영양수액",
    },
    {
        "id": "BM08_REPRODUCTIVE_FEMALE_ACUTE_ABDOMEN",
        "title": "가임기 여성 급성 우하복부 복통·반발통 — hCG 필수 확인, NSAID 차단 및 응급 복증 전원",
        "case": "29세 여성, 아침부터 시작된 급성 우하복부 복통과 구토, 복부 진찰상 반발통(Rebound tenderness) 양성, 메트포르민 복용 중.",
        "expected_triage": "EMERGENCY_IMMEDIATE",
        "expected_rf": "RF10_ACUTE_ABDOMEN_GIBLEED",
        "expected_top_dx": "SYN_ACUTE_ABDOMINAL_PAIN",
        "must_contain_m0": "NSAIDs",
    },
    {
        "id": "BM09_WARD_SEPSIS_NEWS2_HIGH",
        "title": "병동 폐렴 환자 급성 악화(RR 30, SpO2 89%, SBP 84, HR 122, BT 39.2, 의식혼돈) — NEWS2>=7 & Sepsis Bundle",
        "case": "76세 남성, 기침·화농성 객담 폐렴 입원 중 호흡곤란 악화. 혈압 84/50, 맥박 122, 호흡수 30, 산소포화도 89%, 체온 39.2도, 의식 혼돈(Confusion) 발생.",
        "expected_triage": "EMERGENCY_IMMEDIATE",
        "expected_rf": "RF00_NEWS2_CRITICAL",
        "expected_top_dx": "SYN_RESP_PNEUMONIA_BRONCHITIS",
    },
    {
        "id": "BM10_CENTRAL_VERTIGO_STROKE_TRAP",
        "title": "고령 급성 어지럼증 + 구음장애·보행실조 — 뇌졸중(BE-FAST) 킬스위치 및 CT 단독 배제 금지",
        "case": "71세 심방세동 여성, 갑작스러운 빙글빙글 도는 어지럼증과 구토, 발음이 어눌해지는 구음장애 및 혼자 서지 못하는 보행 실조로 내원.",
        "expected_triage": "EMERGENCY_IMMEDIATE",
        "expected_rf": "RF06_STROKE_BEFAST",
        "expected_top_dx": "SYN_DIZZINESS_VERTIGO",
    },
    {
        "id": "BM11_THUNDERCLAP_HEADACHE_SAH",
        "title": "생애 최악의 벼락두통 + 경부강직 — 지주막하출혈 SNOOP10 응급 킬스위치",
        "case": "48세 여성, 운동 중 망치로 맞은 듯한 생애 최악의 두통(벼락두통)과 구역, 뒷목 경부 강직으로 내원.",
        "expected_triage": "EMERGENCY_IMMEDIATE",
        "expected_rf": "RF17_THUNDERCLAP_SAH",
        "expected_top_dx": "SYN_HEADACHE_MIGRAINE_SNOOP",
        "must_contain_m0": "진통제 주사만 투여 후 귀가",
    },
    {
        "id": "BM12_PYELONEPHRITIS_MIMICKING_LBP",
        "title": "발열·배뇨통·늑골척추각 압통(CVAT) 동반 옆구리/허리 통증 — 신우신염 감별 및 척추주사 오진 방지",
        "case": "36세 여성, 어제부터 우측 옆구리 통증과 허리 통증, 38.8도 발열과 오한, 배뇨통 동반, 우측 늑골척추각(CVAT) 타진 압통 양성.",
        "expected_triage": "URGENT_SAME_DAY",
        "expected_top_dx": "SYN_UTI_PYELONEPHRITIS_STONE",
        "must_contain_m0": "단순 요통으로 오인",
    },
    {
        "id": "BM13_CERVICAL_MYELOPATHY_MANIPULATION_BAN",
        "title": "양손 저림 + 젓가락질 어눌함 + 보행 비틀거림 — 경추 척수증 감별 및 도수교정 절대 금지",
        "case": "63세 남성, 2개월 전부터 목 통증과 양손 저림이 시작되고 최근 젓가락질과 단추 채우기가 둔해지며 걸음걸이가 휘청거림(Hoffmann 양성). 경추 도수교정 문의.",
        "expected_triage": "URGENT_SAME_DAY",
        "expected_top_dx": "SYN_CERVICAL_RADICULOMYELOPATHY",
        "must_contain_m0": "도수교정",
    },
    {
        "id": "BM14_ANTICOAGULANT_STENOSIS_PEN_SAFETY",
        "title": "엘리퀴스(Apixaban) 복용 중인 고령 요추관 협착증 환자 — 시술 전 항응고제 휴약 안전 경고 검증",
        "case": "77세 남성, 심방세동으로 엘리퀴스(Apixaban) 복용 중. 50m 걸으면 다리가 터질 듯한 파행과 쪼그려 앉으면 호전되는 요추관 협착증으로 신경성형술 시술 상담 내원.",
        "expected_triage": "OUTPATIENT_STANDARD",
        "expected_top_dx": "SYN_LUMBAR_SPINAL_STENOSIS",
    },
]


def run_benchmark() -> dict:
    engine = MediGeminiAssistLoop()
    results = []
    passed_count = 0

    for bm in BENCHMARK_CASES:
        out = engine.run_assist_loop(bm["case"], max_loops=5)
        draft = out["draft"]
        top_dx = draft["ddx_list"][0]["code"]
        rf_codes = [r["code"] for r in out["red_flags"]]
        wb_score = out["final_audit"]["world_best_score"]

        checks = []
        checks.append(("triage_match", draft["triage_level"] == bm["expected_triage"], f"{draft['triage_level']} vs {bm['expected_triage']}"))
        checks.append(("top_dx_match", top_dx == bm["expected_top_dx"], f"{top_dx} vs {bm['expected_top_dx']}"))
        checks.append(("score_ge_96", wb_score >= 96.0, f"score={wb_score}"))

        if "expected_rf" in bm:
            checks.append(("red_flag_hit", bm["expected_rf"] in rf_codes, f"got={rf_codes}"))
        if "must_contain_m0" in bm:
            m0_joined = " ".join(draft.get("negative_gate_m0", []))
            checks.append(("m0_guard_hit", bm["must_contain_m0"].lower() in m0_joined.lower(), m0_joined[:120]))
        if "must_not_contain_m1" in bm:
            m1_joined = " ".join(draft.get("pharma_m1", []))
            for forbidden in bm["must_not_contain_m1"]:
                checks.append((f"m1_no_{forbidden}", forbidden.lower() not in m1_joined.lower(), m1_joined))

        case_ok = all(c[1] for c in checks)
        if case_ok:
            passed_count += 1

        results.append(
            {
                "id": bm["id"],
                "title": bm["title"],
                "passed": case_ok,
                "initial_loop_score": out["loop_trace"][0]["world_best_score"],
                "final_loop_score": wb_score,
                "loops_executed": out["loops_executed"],
                "top_dx": top_dx,
                "triage": draft["triage_level"],
                "red_flags": rf_codes,
                "failed_checks": [c for c in checks if not c[1]],
            }
        )

    avg_initial = round(sum(r["initial_loop_score"] for r in results) / len(results), 2)
    avg_final = round(sum(r["final_loop_score"] for r in results) / len(results), 2)
    summary = {
        "total_cases": len(BENCHMARK_CASES),
        "passed_cases": passed_count,
        "pass_rate_pct": round(100.0 * passed_count / len(BENCHMARK_CASES), 1),
        "avg_loop1_score": avg_initial,
        "avg_converged_world_best_score": avg_final,
        "score_gain_from_loop": round(avg_final - avg_initial, 2),
        "cases": results,
    }
    return summary


if __name__ == "__main__":
    report = run_benchmark()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["passed_cases"] != report["total_cases"]:
        sys.exit(1)
