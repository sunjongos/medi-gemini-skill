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


class TestMediGeminiAssistLoop(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = MediGeminiAssistLoop()
        self.facade = NDBMediGeminiEngine()

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
        self.assertIn("[3초 직관 브리핑]", md)
        self.assertIn("Must-Not-Miss", md)
        self.assertGreaterEqual(len(self.facade._fetch_ontology()), 20)

    def test_full_10_case_benchmark_100_percent(self) -> None:
        summary = run_benchmark()
        self.assertEqual(summary["passed_cases"], summary["total_cases"], f"Failed benchmark cases: {summary}")
        self.assertGreaterEqual(summary["avg_converged_world_best_score"], 98.0)


if __name__ == "__main__":
    unittest.main()
