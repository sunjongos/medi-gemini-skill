#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Medi-Gemini v7.0 — 1-Click Local Clinical Web App (0-Dependency)
================================================================
Designed for non-developer physicians:
  - Runs 100% locally on 127.0.0.1:8765 using Python standard library (zero external server deps)
  - Connects directly to MediGeminiNeurosymbolicOrchestrator (JEV x Deep Twin x 2025-2026 Multidisciplinary Board)
  - Includes 1-click SOAP / Patient Explanation copy and live Self-Evolution rule learning form
"""

import argparse
import json
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

APP_DIR = Path(__file__).resolve().parent
SKILL_DIR = APP_DIR.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from medi_gemini_neurosymbolic_orchestrator import MediGeminiNeurosymbolicOrchestrator  # noqa: E402

ORCHESTRATOR = MediGeminiNeurosymbolicOrchestrator()

HTML_PAGE = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Medi-Gemini v7.0 — 1인 대학병원 다학제 협진 콘솔</title>
<style>
  :root {
    --bg: #070c17; --panel: #0f172a; --alt: #17233a; --border: #253552;
    --cyan: #38bdf8; --indigo: #818cf8; --green: #10b981; --amber: #f59e0b; --rose: #f43f5e;
    --text: #f8fafc; --muted: #94a3b8;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Pretendard', -apple-system, 'Malgun Gothic', sans-serif; background: var(--bg); color: var(--text); padding: 18px; line-height: 1.55; }
  .top { display: flex; justify-content: space-between; align-items: center; background: var(--panel); border: 1px solid var(--border); border-radius: 14px; padding: 14px 20px; margin-bottom: 16px; }
  .top h1 { font-size: 19px; font-weight: 800; color: var(--cyan); }
  .top p { font-size: 12.5px; color: var(--muted); }
  .badge { background: rgba(16,185,129,.14); border: 1px solid rgba(16,185,129,.4); color: #34d399; padding: 5px 11px; border-radius: 999px; font-size: 12px; font-weight: 700; }
  .grid { display: grid; grid-template-columns: 430px 1fr; gap: 16px; }
  @media (max-width: 1050px) { .grid { grid-template-columns: 1fr; } }
  .card { background: var(--panel); border: 1px solid var(--border); border-radius: 14px; padding: 16px; margin-bottom: 14px; }
  .ctitle { font-size: 14.5px; font-weight: 800; color: var(--cyan); margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }
  .presets { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px; }
  .pbtn { background: var(--alt); color: var(--text); border: 1px solid var(--border); border-radius: 8px; padding: 6px 9px; font-size: 11.8px; cursor: pointer; font-weight: 600; }
  .pbtn:hover { border-color: var(--cyan); color: var(--cyan); }
  textarea, input[type=text] { width: 100%; background: #0a1020; color: var(--text); border: 1px solid var(--border); border-radius: 10px; padding: 10px; font-size: 13px; margin-bottom: 10px; }
  textarea { resize: vertical; }
  .run { width: 100%; padding: 12px; border: none; border-radius: 10px; background: linear-gradient(135deg, #0284c7, #6366f1); color: #fff; font-weight: 800; font-size: 14.5px; cursor: pointer; }
  .run:hover { opacity: .93; }
  .copy { background: var(--alt); color: var(--cyan); border: 1px solid var(--cyan); border-radius: 6px; padding: 4px 10px; font-size: 11.5px; font-weight: 700; cursor: pointer; }
  .banner { padding: 12px 16px; border-radius: 12px; font-weight: 800; font-size: 13.5px; margin-bottom: 14px; border: 1px solid; }
  .banner.ok { background: rgba(16,185,129,.12); border-color: var(--green); color: #6ee7b7; }
  .banner.danger { background: rgba(244,63,94,.18); border-color: var(--rose); color: #fda4af; }
  .baskets { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 14px; }
  @media (max-width: 900px) { .baskets { grid-template-columns: 1fr; } }
  .bkt { background: var(--alt); border: 1px solid var(--border); border-radius: 10px; padding: 12px; font-size: 12.5px; }
  .bkt h3 { font-size: 12.5px; margin-bottom: 6px; }
  .bkt.yes { border-top: 3px solid var(--green); } .bkt.no { border-top: 3px solid var(--rose); } .bkt.tough { border-top: 3px solid var(--amber); }
  .delta { background: #0b1326; border-left: 4px solid var(--indigo); border-radius: 8px; padding: 11px 13px; margin-bottom: 10px; font-size: 12.8px; }
  .delta .old { color: #fda4af; margin-top: 4px; } .delta .new { color: #6ee7b7; margin-top: 4px; } .delta .int { color: #fde68a; margin-top: 4px; }
  pre { background: #090f1d; border: 1px solid var(--border); border-radius: 10px; padding: 12px; white-space: pre-wrap; font-family: Consolas, monospace; font-size: 12.4px; color: #e2e8f0; }
  ul { padding-left: 18px; font-size: 13px; } li { margin-bottom: 5px; }
</style>
</head>
<body>
<div class="top">
  <div>
    <h1>🏥 Medi-Gemini v7.0 — 1인 대학병원 다학제 협진 콘솔</h1>
    <p>JEV Router × Clinical Deep Twin × 2025~2026 타과 최신 표준 Delta × 17대 Red Flag & 약물 방화벽 (100% 로컬 실행)</p>
  </div>
  <span class="badge">● Local Zero-PHI Engine Live</span>
</div>

<div class="grid">
  <div>
    <div class="card">
      <div class="ctitle">📥 진료실 빠른 입력 (복사·붙여넣기)</div>
      <div class="presets">
        <button class="pbtn" onclick="preset('dm_spine')">1. 당뇨(자디앙+마운자로)+프롤리아 수술전</button>
        <button class="pbtn" onclick="preset('charcot')">2. 당뇨발 발적·부종(샤르코 감별)</button>
        <button class="pbtn" onclick="preset('knee')">3. 50대 무릎 뒤 '뚝'(기시부 파열)</button>
        <button class="pbtn" onclick="preset('ckd_pgx')">4. ARB+이뇨제+eGFR22+HLA-B*58:01</button>
        <button class="pbtn" style="border-color:#f43f5e;color:#fda4af;" onclick="preset('emer')">🚨 수술후 2일차 급성 족하수</button>
      </div>
      <textarea id="caseText" rows="5" placeholder="환자 증상, 복용약(당뇨약·혈압약·항혈전제·골다공증약), 검사수치(eGFR, K+ 등)를 자유롭게 입력하세요."></textarea>
      <textarea id="ehrText" rows="3" placeholder="(선택) 과거 의무기록 / 알레르기 / 이전 검사 추세 붙여넣기"></textarea>
      <button class="run" onclick="runAnalyze()">⚡ 3초 대학병원 다학제 협진 추론 실행</button>
    </div>

    <div class="card">
      <div class="ctitle">🧬 새 최신 의학 규칙 1-클릭 자가학습 (Self-Evolve)</div>
      <input type="text" id="l_spec" placeholder="진료과 (예: 내분비내과 / 족부정형외과)">
      <input type="text" id="l_topic" placeholder="주제 (예: 최신 당뇨 신약 수술 전 휴약 규칙)">
      <input type="text" id="l_cues" placeholder="감지 키워드 쉼표 구분 (예: 신약명, 당뇨수술)">
      <input type="text" id="l_old" placeholder="❌ 예전 관행/함정">
      <input type="text" id="l_new" placeholder="✅ 2026 최신 표준 의사결정">
      <input type="text" id="l_int" placeholder="🔗 척추/정형외과 교차 주의사항">
      <button class="copy" style="width:100%;padding:9px;" onclick="learnRule()">💾 온톨로지 DB + LLM-Wiki에 영구 학습</button>
      <div id="learnMsg" style="font-size:12px;color:#34d399;margin-top:6px;"></div>
    </div>
  </div>

  <div>
    <div id="banner" class="banner ok">좌측에서 증례를 선택하거나 입력한 뒤 [추론 실행]을 눌러주세요.</div>

    <div class="baskets">
      <div class="bkt yes"><h3>🟢 YES ($M=1$ 실행)</h3><div id="bYes">-</div></div>
      <div class="bkt no"><h3>🔴 NO ($M=0$ 금기·차단)</h3><div id="bNo">-</div></div>
      <div class="bkt tough"><h3>🟡 TOO TOUGH (전문의 결단)</h3><div id="bTough">-</div></div>
    </div>

    <div class="card">
      <div class="ctitle"><span>🏥 1인 대학병원 다학제 협진 패널 (예전 관행 vs 2025~2026 최신 표준)</span><span id="routeBadge" style="font-size:11.5px;color:var(--muted);"></span></div>
      <div id="mdBoard">해당 타과 최신 가이드라인 협진 항목이 여기에 표시됩니다.</div>
    </div>

    <div class="card">
      <div class="ctitle">🧠 베이즈 감별진단(Top-3 & Must-Not-Miss) · 능동 문진</div>
      <div id="ddxBox">-</div>
    </div>

    <div class="card">
      <div class="ctitle"><span>📋 EMR 복사용 SOAP 차트 & 2026 심사 방어</span><button class="copy" onclick="copyEl('soapBox')">📋 원클릭 복사</button></div>
      <pre id="soapBox">-</pre>
    </div>

    <div class="card">
      <div class="ctitle"><span>🗣️ 환자 안심 설명 비유 스크립트</span><button class="copy" onclick="copyEl('metaphorBox')">💬 설명 복사</button></div>
      <pre id="metaphorBox">-</pre>
    </div>
  </div>
</div>

<script>
const PRESETS = {
  dm_spine: {
    case: "68세 여성, L4-5 중증 척추관 협착증(50m 파행)으로 BESS 내시경 감압술 예정. 당뇨약 자디앙(SGLT2i)과 비만주사 마운자로(GLP-1) 투여 중이며, 골다공증으로 6개월 전 프롤리아(데노수맙) 맞고 치과 치료 때문에 중단 고민 중.",
    ehr: "2025년 eGFR 68 -> 2026년 eGFR 52."
  },
  charcot: {
    case: "61세 당뇨 15년차 남성(말초신경병증 동반), 1주 전부터 우측 발등과 발목이 붉고 뜨겁게 부었는데 통증은 거의 없음. 로컬에서 봉와직염으로 항생제만 먹고 계속 걸어다님.",
    ehr: "HbA1c 8.6%, 당뇨병성 발 감각 저하."
  },
  knee: {
    case: "57세 여성, 3일 전 쪼그려 앉아 집안일 하다 무릎 뒤 안쪽에서 '뚝' 소리가 난 뒤 계단 내려갈 때 극심한 무릎 통증과 부종 발생. 반월상연골 파열 의심.",
    ehr: "특이 기저질환 없음."
  },
  ckd_pgx: {
    case: "78세 남성, 좌측 L5 타는 듯한 방사통(VAS 8), 고혈압약(발사르탄 ARB + 이뇨제 복합제) 복용 중, 만성콩팥병 eGFR 22, HLA-B*58:01 양성, 동적 X-ray 전방전위 4.5mm. 세레콕시브와 알로푸리놀 처방 문의.",
    ehr: "2024년 설파제(Sulfa) 알레르기 발진 병력. Hb 13.5 -> Hb 11.7 감소."
  },
  emer: {
    case: "64세 여성, 요추 감압 수술 2일차 병동 입원 중 갑작스러운 우측 족하수(Foot drop, SMC Grade 2) 및 창상 부위 심한 팽만 통증 발생.",
    ehr: "수술 전 아스피린 5일 중단 후 시행."
  }
};

function preset(k) {
  document.getElementById('caseText').value = PRESETS[k].case;
  document.getElementById('ehrText').value = PRESETS[k].ehr;
  runAnalyze();
}

async function runAnalyze() {
  const caseText = document.getElementById('caseText').value.trim();
  const ehrText = document.getElementById('ehrText').value.trim();
  if (!caseText) return;
  const res = await fetch('/api/analyze', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({case_text: caseText, ehr_timeline: ehrText})
  });
  const data = await res.json();
  const cl = data.closed_loop_assist;
  const dt = data.deep_twin;
  const caps = data.med_gemini_capabilities;
  const rfs = cl.red_flags || [];

  const banner = document.getElementById('banner');
  if (rfs.length > 0) {
    banner.className = 'banner danger';
    banner.innerText = `🚨 [응급 킬스위치 발동] ${rfs.map(r => r.title + ' (' + r.time_target + ')').join(' | ')} — Score ${cl.final_audit.world_best_score}/100`;
  } else {
    banner.className = 'banner ok';
    banner.innerText = `✅ [17대 Red Flag 통과 | NEWS2=${cl.extracted_state.news2_score}] ${dt.execution_gate} | NDB Index=${dt.ndb_value_index} | Score ${cl.final_audit.world_best_score}/100`;
  }

  document.getElementById('routeBadge').innerText = `JEV Router: ${data.jev_router.primary_route} (${data.jev_router.router_latency_ms}ms)`;
  document.getElementById('bYes').innerHTML = '<ul>' + dt.munger_3_basket.YES_M1_Preserve_Execute.map(x => `<li>${x}</li>`).join('') + '</ul>';
  document.getElementById('bNo').innerHTML = '<ul>' + (dt.munger_3_basket.NO_M0_Discard_Block.length ? dt.munger_3_basket.NO_M0_Discard_Block.map(x => `<li>${x}</li>`).join('') : '<li>차단 항목 없음</li>') + '</ul>';
  document.getElementById('bTough').innerHTML = '<ul>' + (dt.munger_3_basket.TOO_TOUGH_Physician_Gate.length ? dt.munger_3_basket.TOO_TOUGH_Physician_Gate.map(x => `<li>${x}</li>`).join('') : '<li>표준 프로토콜 범위 내</li>') + '</ul>';

  const mdList = caps['5_multidisciplinary_2026_consult_board'] || [];
  document.getElementById('mdBoard').innerHTML = mdList.length
    ? mdList.map(m => `<div class="delta"><b>🩺 [${m.specialty}] ${m.topic}</b> <span style="color:var(--muted);font-size:11px;">(${m.source_ref})</span><div class="old">❌ 예전 관행: ${m.old_practice}</div><div class="new">✅ 2025~2026 최신 표준: ${m.latest_2026_standard}</div><div class="int">🔗 척추/정형외과 교차 의사결정: ${m.spine_ortho_interaction}</div></div>`).join('')
    : '<div style="color:var(--muted);font-size:12.5px;">특이 타과 최신 Delta 트리거 없음 (표준 다학제 감별진단 적용)</div>';

  const ddx = cl.draft.ddx_list || [];
  const qList = cl.draft.missing_cues_questions || [];
  document.getElementById('ddxBox').innerHTML =
    '<ul>' + ddx.map((d,i) => `<li><b>${i+1}. ${d.name_ko}</b> (P≈${Math.round(d.posterior_prob*100)}%, ${d.specialty})</li>`).join('') + '</ul>' +
    `<div style="margin-top:8px;color:#fda4af;font-size:12.5px;"><b>⚠️ Must-Not-Miss:</b> ${(cl.draft.must_not_miss_explicit||[]).join(', ')}</div>` +
    `<div style="margin-top:8px;color:#93c5fd;font-size:12.5px;"><b>🔍 추가 확인 질문(VOI):</b><ul>${qList.map(q=>`<li>${q}</li>`).join('')}</ul></div>`;

  document.getElementById('soapBox').innerText = cl.draft.charting_template + '\n\n[심사·윤리] ' + cl.draft.hira_and_consent_note;
  document.getElementById('metaphorBox').innerText = ddx[0] ? ddx[0].patient_metaphor : '-';
}

async function learnRule() {
  const payload = {
    specialty: document.getElementById('l_spec').value.trim(),
    topic: document.getElementById('l_topic').value.trim(),
    trigger_cues: document.getElementById('l_cues').value.split(',').map(s => s.trim()).filter(Boolean),
    old_practice: document.getElementById('l_old').value.trim(),
    latest_2026_standard: document.getElementById('l_new').value.trim(),
    spine_ortho_interaction: document.getElementById('l_int').value.trim()
  };
  if (!payload.specialty || !payload.topic || !payload.latest_2026_standard) {
    document.getElementById('learnMsg').innerText = '진료과, 주제, 2026 최신 표준을 입력해 주세요.';
    return;
  }
  const res = await fetch('/api/learn', {
    method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)
  });
  const out = await res.json();
  document.getElementById('learnMsg').innerText = `✅ 자가학습 완료 (${out.delta_id}) — 이제 즉시 진료 추론에 반영됩니다!`;
}

function copyEl(id) {
  navigator.clipboard.writeText(document.getElementById(id).innerText);
  alert('클립보드에 복사되었습니다!');
}

window.onload = () => preset('dm_spine');
</script>
</body>
</html>
"""


class MediGeminiHTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        return  # keep console clean

    def _send_json(self, data: Dict[str, Any], status: int = 200) -> None:
        raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:
        if self.path in ("/", "/index.html"):
            raw = HTML_PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
        elif self.path == "/api/health":
            self._send_json({"status": "ok", "engine": "Medi-Gemini v7.0 Local Multidisciplinary Consult Server"})
        else:
            self._send_json({"error": "not_found"}, status=404)

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        body = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        if self.path == "/api/analyze":
            out = ORCHESTRATOR.orchestrate(
                case_text=body.get("case_text", ""),
                ehr_timeline=body.get("ehr_timeline") or None,
                modality_hint=body.get("modality_hint") or None,
            )
            self._send_json({k: v for k, v in out.items() if k != "markdown_report"})
        elif self.path == "/api/learn":
            res = ORCHESTRATOR.capabilities.learn_new_guideline_delta(
                specialty=body.get("specialty", "다학제"),
                topic=body.get("topic", ""),
                trigger_cues=body.get("trigger_cues", []),
                old_practice=body.get("old_practice", ""),
                latest_2026_standard=body.get("latest_2026_standard", ""),
                spine_ortho_interaction=body.get("spine_ortho_interaction", ""),
            )
            self._send_json(res)
        else:
            self._send_json({"error": "not_found"}, status=404)


def run_server(port: int = 8765, open_browser: bool = True) -> None:
    server = ThreadingHTTPServer(("127.0.0.1", port), MediGeminiHTTPHandler)
    url = f"http://127.0.0.1:{port}"
    print(f"🏥 [Medi-Gemini v7.0] 1인 대학병원 다학제 협진 웹 앱 가동: {url}")
    if open_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Medi-Gemini 로컬 서버를 종료합니다.")
        server.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Medi-Gemini v7.0 1-Click Local Clinical Web App")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    run_server(port=args.port, open_browser=not args.no_browser)
