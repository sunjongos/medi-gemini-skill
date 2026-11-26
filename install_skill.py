#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Medi-Gemini Skill v7.0 — 1-Line Complete Installer
Installs:
  1. Medi-Gemini v7.0 Neurosymbolic Skill container (.agents/skills/ndb_medi_gemini_engine/)
  2. /medi-gemini Slash Workflow (.agents/workflows/medi-gemini.md)
  3. 1-Click Local Multidisciplinary Clinic Web App (app/ + launch_medi_gemini_app.bat)
  4. High-Contrast Custom Desktop Shortcut (Windows Desktop: Medi-Gemini 다학제협진.lnk)
"""

import argparse
import shutil
import subprocess
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
    "launch_medi_gemini_app.bat",
    "🩺_MediGemini_다학제협진_실행.bat",
    "NDB_Medi_Gemini_Clinical_Assist_Console.html",
    "Choi_3x3_Pain_Matrix_Interactive_Dashboard.html",
    "NDB_Medi_Gemini_Medical_AI_Console.html",
    "NDB_Medi_Gemini_Medical_Ontology_Master.html",
]

SUBDIRS = ["app", "assets", "scripts", "wiki", "workflows", "references", "tests", "dashboards"]


def create_windows_desktop_shortcut(skill_dir: Path) -> None:
    if sys.platform != "win32":
        return
    target_bat = skill_dir / "launch_medi_gemini_app.bat"
    ico_path = skill_dir / "assets" / "medi_gemini_icon.ico"
    if not target_bat.exists():
        return
    ps_script = (
        "$WshShell = New-Object -ComObject WScript.Shell; "
        "$desktop = [Environment]::GetFolderPath('Desktop'); "
        "$lnk = Join-Path $desktop 'Medi-Gemini 다학제협진.lnk'; "
        "$sc = $WshShell.CreateShortcut($lnk); "
        f"$sc.TargetPath = '{target_bat}'; "
        f"$sc.WorkingDirectory = '{skill_dir}'; "
        "$sc.Description = 'Medi-Gemini v7.0 - 1인 대학병원 다학제 협진 콘솔 (로컬 실행)'; "
        + (f"$sc.IconLocation = '{ico_path},0'; " if ico_path.exists() else "")
        + "$sc.Save(); ie4uinit.exe -show"
    )
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], check=True)
        print("   ✅ 바탕화면 바로가기 아이콘 생성 완료: Medi-Gemini 다학제협진.lnk")
    except Exception as e:
        print(f"   ⚠️ 바탕화면 바로가기 생성 건너뜀: {e}")


def install(target_skill_dir: Path, install_workflow: bool = True, create_shortcut: bool = True) -> None:
    print(f"📦 [Medi-Gemini v7.0] 1인 대학병원 다학제 진료 패키지 설치 시작 -> {target_skill_dir}")
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

    # Install /medi-gemini slash workflow into sibling .agents/workflows/ when installing into a workspace
    wf_src = CURRENT_DIR / "workflows" / "medi-gemini.md"
    if install_workflow and wf_src.exists() and target_skill_dir.parent.name == "skills":
        wf_dir = target_skill_dir.parent.parent / "workflows"
        wf_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(wf_src, wf_dir / "medi-gemini.md")
        print(f"   ✅ /medi-gemini 워크플로우 등록: {wf_dir / 'medi-gemini.md'}")

    if create_shortcut:
        create_windows_desktop_shortcut(target_skill_dir)

    print(f"🎉 [설치 완료] Medi-Gemini v7.0 스킬·웹앱·바로가기 장착 완료: {target_skill_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Install Medi-Gemini v7.0 Skill, Web App & Desktop Shortcut")
    parser.add_argument("--target", type=str, default=None, help="Custom target directory")
    parser.add_argument("--no-shortcut", action="store_true", help="Skip Windows Desktop shortcut creation")
    args = parser.parse_args()

    if args.target:
        target = Path(args.target).expanduser().resolve()
        install(target, install_workflow=False, create_shortcut=False)
    else:
        home = Path.home()
        candidates = [
            home / "Desktop" / "luca연구에이전트",
            home / "Desktop" / "AIagent_antigravity",
        ]
        base = next((c for c in candidates if c.exists()), candidates[0])
        target = base / ".agents" / "skills" / "ndb_medi_gemini_engine"
        install(target, install_workflow=True, create_shortcut=not args.no_shortcut)


if __name__ == "__main__":
    main()
