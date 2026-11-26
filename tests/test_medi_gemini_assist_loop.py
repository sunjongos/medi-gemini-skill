#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_DIR))
sys.path.insert(0, str(SKILL_DIR / "scripts"))

from ndb_medi_gemini_agent import NDBMediGeminiEngine  # noqa: E402
from benchmark_assist_loop import run_benchmark  # noqa: E402
from medi_gemini_assist_loop import ClinicalFeatureExtractor, MediGeminiAssistLoop  # noqa: E402
from medi_gemini_neurosymbolic_orchestrator import MediGeminiNeurosymbolicOrchestrator  # noqa: E402


class TestMediGeminiAssistLoop(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = MediGeminiAssistLoop()
        self.facade = NDBMediGeminiEngine()
        self.orchestrator = MediGeminiNeurosymbolicOrchestrator()

    def test_news2_calculation_accuracy(self) -> None:
        score, comp = ClinicalFeatureExtractor.compute_news2(
            rr=30, spo2=89, sbp=84, hr=122, bt=39.2, altered_mental=True
        )
        self.assertGreaterEqual(score, 15)
        self.assertEqual(comp["RR"], 3)
        self.assertEqual(comp["SpO2"], 3)
        self.assertEqual(comp["SBP"], 3)
        self.assertEqual(comp["Consciousness"], 3)

    def test_sublingual_nifedipine_and_hyperkalemia_guard(self) -> None:
        case = "72세 남성 병동 환자, 혈압 195/110, 혈청 K+ 6.4 mEq/L, 심전도 Tent-T 소견. 설하 니페디핀 투여 문의."
        res = self.engine.run_assist_loop(case)
        rf_codes = {r["code"] for r in res["red_flags"]}
        self.assertIn("RF15_HYPERKALEMIA", rf_codes)
        m0_text = " ".join(res["draft"]["negative_gate_m0"])
        self.assertIn("Nifedipine", m0_text)
        self.assertGreaterEqual(res["final_audit"]["world_best_score"], 96.0)

    def test_anaphylaxis_epinephrine_im_protocol(self) -> None:
        case = "45세 여성, 진통제 주사 후 호흡곤란, 전신 두드러기와 어지러움, 천명음과 저혈압(혈압 80/50) 발생."
        res = self.engine.run_assist_loop(case)
        rf_codes = {r["code"] for r in res["red_flags"]}
        self.assertIn("RF12_ANAPHYLAXIS", rf_codes)
        self.assertIn("Epinephrine", res["markdown_report"])
        self.assertIn("근육주사(IM)", res["markdown_report"])

    def test_backward_compatible_facade(self) -> None:
        md = self.facade.analyze_clinical_case("55세 남성, 좌측 L5 방사통 및 다리 저림, VAS 7, 근력 정상.")
        self.assertTrue("[3초 직관 브리핑]" in md or "[3초 직관 진료 브리핑]" in md)
        self.assertIn("M=1", md)
        self.assertGreaterEqual(len(self.facade._fetch_ontology()), 9)

    def test_full_14_case_benchmark_100_percent(self) -> None:
        summary = run_benchmark()
        self.assertEqual(summary["passed_cases"], summary["total_cases"], f"Failed benchmark cases: {summary}")
        self.assertGreaterEqual(summary["avg_converged_world_best_score"], 98.0)

    def test_jev_deeptwin_pgx_ehr_vision_orchestrator(self) -> None:
        case = (
            "78세 남성, 좌측 L5 타는 듯한 방사통(VAS 8), 만성콩팥병(eGFR 22), "
            "HLA-B*58:01 양성 및 G6PD 결핍, 요추 동적 X-ray상 전방전위 4.5mm, "
            "세레콕시브·알로푸리놀 및 고용량 비타민C 수액 문의."
        )
        ehr_history = "2024년 초진기록: 설파제(Sulfa) 복용 후 발진 알레르기. 2025년 eGFR 45 -> 2026년 eGFR 22 감소. Hb 13.8 -> Hb 11.9 감소."
        out = self.orchestrator.orchestrate(case_text=case, ehr_timeline=ehr_history, modality_hint="xray")

        # 1. JEV Router multi-capability activation
        route_ids = {c["route_id"] for c in out["jev_router"]["activated_capabilities"]}
        self.assertIn("MG_ROUTE_06_GENOMICS_PGX", route_ids)
        self.assertIn("MG_ROUTE_03_LONG_EHR", route_ids)

        # 2. PGx CPIC firewall
        pgx_genes = {p["gene_biomarker"] for p in out["med_gemini_capabilities"]["4_pharmacogenomics_pgx"]}
        self.assertTrue(any("HLA-B*58:01" in g for g in pgx_genes))
        self.assertTrue(any("G6PD" in g for g in pgx_genes))

        # 3. Long-EHR Needle-in-a-Haystack + FHIR R4 Bundle
        ehr_out = out["med_gemini_capabilities"]["2_long_context_ehr_and_fhir"]
        self.assertGreaterEqual(ehr_out["needle_count"], 3)
        self.assertEqual(ehr_out["fhir_r4_bundle"]["resourceType"], "Bundle")

        # 4. 2D/3D Vision Symbolic Thresholds
        vis_out = out["med_gemini_capabilities"]["3_multimodal_2d_3d_vision"]
        self.assertTrue(any("4.5mm" in s for s in vis_out["extracted_symbolic_findings"]))

        # 5. Deep Twin Munger 3-Basket & NDB Value Index
        dt = out["deep_twin"]
        self.assertGreaterEqual(dt["ndb_value_index"], 0.95)
        no_joined = " ".join(dt["munger_3_basket"]["NO_M0_Discard_Block"])
        self.assertIn("Allopurinol", no_joined)
        self.assertIn("NSAIDs", no_joined)


if __name__ == "__main__":
    unittest.main()
