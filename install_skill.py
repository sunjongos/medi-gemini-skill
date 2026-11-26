#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Medi-Gemini Skill v5.0 — 1-Line Portable Skill Installer
Installs the complete Medi-Gemini Closed-Loop Clinical Assist skill container
into Antigravity / Claude Code workspace skill directories.
"""

import argparse
import shutil
import sys
from pathlib import Path

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

CURRENT_DIR = Path(__file__).resolve().parent

ROOT_FILES = [
    "SKILL.md",
    "README.md",
    "LICENSE",
    "requirements.txt",
    "ndb_medi_gemini_agent.py",
    "medi_gemini_knowledge.db",
    "NDB_Medi_Gemini_Clinical_Assist_Console.html",
    "Choi_3x3_Pain_Matrix_Interactive_Dashboard.html",
    "NDB_Medi_Gemini_Medical_AI_Console.html",
    "NDB_Medi_Gemini_Medical_Ontology_Master.html",
]

SUBDIRS = ["scripts", "references", "tests", "dashboards"]


def install(target_skill_dir: Path) -> None:
    print(f"📦 [Medi-Gemini v5.0] 스킬 컨테이너 설치 시작 -> {target_skill_dir}")
    target_skill_dir.mkdir(parents=True, exist_ok=True)

    for fname in ROOT_FILES:
        src = CURRENT_DIR / fname
        if src.exists() and src.resolve() != (target_skill_dir / fname).resolve():
            shutil.copy2(src, target_skill_dir / fname)
            print(f"   ✅ 파일 복사: {fname}")

    for dname in SUBDIRS:
        src_dir = CURRENT_DIR / dname
        dst_dir = target_skill_dir / dname
        if src_dir.exists() and src_dir.resolve() != dst_dir.resolve():
            shutil.copytree(
                src_dir,
                dst_dir,
                dirs_exist_ok=True,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
            print(f"   ✅ 디렉터리 동기화: {dname}/")

    print(f"🎉 [설치 완료] Medi-Gemini v5.0 스킬이 장착되었습니다: {target_skill_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Install Medi-Gemini v5.0 Agent Skill")
    parser.add_argument(
        "--target",
        type=str,
        default=None,
        help="Custom target skill directory (defaults to ~/Desktop/luca연구에이전트/.agents/skills/ndb_medi_gemini_engine)",
    )
    args = parser.parse_args()

    if args.target:
        target = Path(args.target).expanduser().resolve()
    else:
        home = Path.home()
        candidates = [
            home / "Desktop" / "luca연구에이전트",
            home / "Desktop" / "AIagent_antigravity",
        ]
        base = next((c for c in candidates if c.exists()), candidates[0])
        target = base / ".agents" / "skills" / "ndb_medi_gemini_engine"

    install(target)


if __name__ == "__main__":
    main()
