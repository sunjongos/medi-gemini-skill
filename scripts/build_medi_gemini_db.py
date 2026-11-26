#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Medi-Gemini v5.0 Unified Clinical Ontology & Safety SQLite Builder
0-Dependency deterministic Left-Brain knowledge base covering:
1. medi_gemini_ontology (Knowledge Graph Triples - backward compatible + expanded)
2. red_flag_killswitch (16 Emergency & Ward Kill-Switch Guardrails)
3. clinical_syndromes_ddx (Multi-specialty Bayesian DDx & Stepwise Treatment Pathways)
4. drug_safety_formulary (Renal eGFR, Geriatric, DDI, Chronopharmacology & Contraindications)
5. hira_reimbursement_rules (2026 HIRA, Informed Consent & Medical-Legal Documentation)
6. assist_loop_audit_log (Auditable Traceability for Closed-Loop Assist)
"""

import json
import sqlite3
import sys
from pathlib import Path

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SKILL_DIR = Path(__file__).resolve().parent.parent
DB_PATH = SKILL_DIR / "medi_gemini_knowledge.db"


ONTOLOGY_TRIPLES = [
    ("3x3 Pain Matrix", "DRG Gate (Cell A1)", "EXCITES_VIA", "NaV1.7 / NaV1.8 Up-regulation", "말초 유창성 모세혈관(Fenestrated capillary) 염증 노출로 이소성 자발 발화 유발"),
    ("3x3 Pain Matrix", "Spinal Horn (Cell A2)", "EXCITES_VIA", "Presynaptic CaV alpha2-delta-1 & NMDA", "시냅스전 글루타메이트 과방출 및 중추 바람개비(Wind-up) 현상 유발"),
    ("3x3 Pain Matrix", "Supraspinal Cortex (Cell A3)", "EXCITES_VIA", "Thalamocortical Hyperexcitability", "시상-피질 감각 증폭 및 과각성 유발"),
    ("3x3 Pain Matrix", "DRG Gate (Cell B1)", "DISINHIBITS_VIA", "Satellite Glial GABA Tonic Loss", "DRG 위성교세포 억제 완충 소실"),
    ("3x3 Pain Matrix", "Spinal Horn (Cell B2)", "DISINHIBITS_VIA", "KCC2 Down-regulation & Cl- Reversal", "세포내 Cl- 축적으로 GABAA 억제 신호가 탈분극 흥분으로 역전"),
    ("3x3 Pain Matrix", "Brainstem (Cell B3)", "DISINHIBITS_VIA", "PAG-RVM Descending Inhibition Collapse", "노르에피네프린/세로토닌 하행성 진통 경로 붕괴 (SNRI 표적)"),
    ("3x3 Pain Matrix", "Peripheral Nerve (Cell C1)", "TRANSMITS_VIA", "A-delta / C-Fiber & HCN Ih Oscillation", "소섬유 역치 저하로 이질통(Allodynia) 및 전격통 전달"),
    ("3x3 Pain Matrix", "Spinal Horn (Cell C2)", "TRANSMITS_VIA", "Spinothalamic Tract Spinal LTP", "척수 2차 투사 신경원의 시냅스 장기강화(LTP) 고착"),
    ("3x3 Pain Matrix", "Supraspinal DMN (Cell C3)", "REMODELS_VIA", "mPFC-Insula-Amygdala Bayesian Prior", "통증의 자아화 및 파국화 기대(Prior) 고착"),
    ("Bayesian NeuroMatrix", "Perceived Pain Posterior", "PROPORTIONAL_TO", "Peripheral Likelihood x Brain Threat Prior", "MRI 병변 크기와 통증 강도 불일치 설명 및 공포 소거 치료 근거"),
    ("Spine Hygiene", "Lumbar Flexion Load", "CAUSES", "Intradiscal Pressure Spike & Cytokine Leak", "섬유륜 균열 틈으로 PLA2/TNF-alpha 염증 수프 분출 -> 굴곡 금지 및 맥켄지 신전 필수"),
    ("Chronopharmacology", "Evening Duloxetine (20:00)", "ALIGNS_TMAX_WITH", "03:00-04:00 Cytokine & Pain Peak", "복용 6시간 후 Tmax 도달로 새벽 통증 피크 및 하행 억제계 선제 방어"),
    ("Chronopharmacology", "Bedtime Pregabalin (HS)", "RESTORES", "Slow-Wave Sleep & Nocturnal Synaptic Calm", "야간 발작성 신경병증 통증 차단 및 서파 수면 복원"),
    ("Interventional Pain", "Balloon-PEN / C-PEN", "PERFORMS", "Mechanical Adhesiolysis + Cytokine Washout", "추간공/경막외 유착 물리 박리 및 고장성 식염수 염증 세척 리셋"),
    ("MIS Spine Surgery", "BESS Biportal Endoscopy", "PRESERVES", "80%+ Facet Joint & Paraspinal Muscle", "수중 연속 관류 시야 하 황색인대/탈출 수핵만 핀포인트 감압"),
    ("Ward Safety", "Post-op SMC Drop", "TRIGGERS", "1-6h Emergency MRI & Hematoma Decompression", "경막외 혈종 골든타임 내 감압으로 영구 신경마비 예방"),
    ("Ward Safety", "NEWS2 >= 7", "TRIGGERS", "Immediate Rapid Response Team & ABCDE", "급성 전신 악화 조기 포착 및 패혈증/호흡부전 사망률 감소"),
    ("Cardiology Emergency", "Chest Pain Arrival", "REQUIRES_WITHIN_10MIN", "12-Lead ECG & Serial High-Sensitivity Troponin", "STEMI/NSTEMI 및 대동맥박리 즉시 감별"),
    ("Renal Safety", "eGFR < 30 mL/min/1.73m2", "CONTRAINDICATES", "Systemic NSAIDs & Unadjusted Gabapentinoids", "급성 신손상(AKI) 및 신경독성/의식저하 예방"),
    ("Hypertension Safety", "Severe Inpatient HTN", "CONTRAINDICATES", "Sublingual Nifedipine", "급격한 혈압 강하로 인한 뇌경색/심근허혈 유발 위험으로 절대 금기"),
    ("Radiology Safety", "Iodinated IV Contrast + eGFR < 60", "REQUIRES", "Metformin Hold 48h & Hydration Check", "조영제 유발 신병증 및 유산산증(Lactic Acidosis) 예방"),
    ("Anticoagulation Safety", "Neuraxial PEN / Spine Surgery", "REQUIRES", "Anticoagulant Washout Verification", "Rivaroxaban/Apixaban 72h, Clopidogrel 5-7d 중단 미확인 시 경막외 혈종 위험"),
    ("HIRA 2026", "Ja-46 Spine Surgery Claim", "REQUIRES", "6-Week Conservative Record OR SMC <= 3 / CES", "심평원 삭감 제로 및 적정 진료 컴플라이언스 보장"),
    ("Medical Ethics", "Non-Covered IV / Procedure", "REQUIRES", "Purpose-Limit-Cost Explanation & Choice/Refusal Log", "환자 자기결정권 존중 및 민원/법적 리스크 원천 차단"),
]


RED_FLAGS = [
    {
        "code": "RF01_CES",
        "title": "마미총 증후군 (Cauda Equina Syndrome)",
        "category": "SPINE_NEURO",
        "severity": "CRITICAL_IMMEDIATE",
        "cues": ["배뇨장애", "배뇨 곤란", "요폐", "소변이 안", "잔뇨", "변실금", "요실금", "배변장애", "안장", "회음부 감각", "saddle", "urinary retention", "fecal incontinence", "항문 괄약근"],
        "action": "일반 외래/보존치료 즉시 중단 -> 응급 요추 MRI 촬영, 방광 잔뇨량(PVR) 측정, 척추외과 당직 호출 및 24시간 이내 긴급 감압술(BESS/감압술) 준비",
        "time_target": "즉시 평가 / 24시간 내 감압술",
    },
    {
        "code": "RF02_POSTOP_HEMATOMA",
        "title": "수술 후 급성 경막외 혈종 / SMC 마비 진행 (Post-op Epidural Hematoma)",
        "category": "SPINE_POSTOP",
        "severity": "CRITICAL_IMMEDIATE",
        "cues": ["수술 후 마비", "수술 후 근력", "수술 후 족하수", "수술후 족하수", "수술 3일차", "수술 1일차", "수술 2일차", "수술 직후", "경막외 혈종", "smc 저하", "epidural hematoma"],
        "action": "집도의 즉시 호출(Stat), 창상 및 배액관(Hemovac) 개통 확인, 응급 MRI 촬영 및 1~6시간 골든타임 내 응급 혈종제거술 준비 (지연 관찰 절대 금지)",
        "time_target": "1시간 내 수술 결정 / 6시간 내 감압",
    },
    {
        "code": "RF03_CERVICAL_AIRWAY",
        "title": "경추 수술 후 기도 폐쇄 위험 혈종 (Post-Cervical Airway Compromise)",
        "category": "AIRWAY_SURGERY",
        "severity": "CRITICAL_IMMEDIATE",
        "cues": ["경추 수술 후 호흡곤란", "목 수술 후 호흡곤란", "목 부종", "경부 부종", "연하곤란", "흡기성 천명", "stridor", "cervical hematoma"],
        "action": "영상실 이동 금지! 침상(Bedside)에서 즉시 봉합사 발사 및 창상 개방으로 기도 압박 해소 + 산소 공급 + 마취통증의학과 기관삽관 대기",
        "time_target": "즉시 침상 개방 (수분 이내)",
    },
    {
        "code": "RF04_SEVERE_MOTOR_DEFICIT",
        "title": "급성 중증 운동마비 / 족하수 (Acute Progressive Motor Deficit SMC <= 3)",
        "category": "SPINE_NEURO",
        "severity": "CRITICAL_URGENT",
        "cues": ["족하수", "foot drop", "발목이 안 올라", "엄지발가락 힘", "smc 0", "smc 1", "smc 2", "smc 3", "grade 0", "grade 1", "grade 2", "grade 3", "motor 2", "motor 3", "진행성 마비", "다리에 힘이 빠"],
        "action": "보존치료 6주 대기 예외(조기 수술 적응증) -> 당일 정밀 MRI 확인 후 조기 최소침습 신경감압술(BESS 등) 검토",
        "time_target": "당일 정밀 MRI / 24~48시간 내 감압 검토",
    },
    {
        "code": "RF05_ACS_AORTIC",
        "title": "급성 관상동맥 증후군 / 대동맥박리 의심 (ACS / Aortic Dissection)",
        "category": "CARDIOVASCULAR",
        "severity": "CRITICAL_IMMEDIATE",
        "cues": ["흉통", "가슴 통증", "가슴이 쥐어짜", "식은땀", "좌측 팔 방사통", "턱 방사통", "찢어지는 듯한 등 통증", "찢어지는 흉통", "st 상승", "stemi", "트로포닌 상승", "troponin 상승", "chest pain"],
        "action": "도착 10분 이내 12유도 심전도(ECG) + 고감도 Troponin + 활력징후/양팔 혈압 측정 + 산소/모니터링 후 ST상승·혈역학 불안정·대동맥박리 의심 시 즉시 119 상급병원 심혈관센터 전원",
        "time_target": "10분 내 ECG / 즉시 응급 전원",
    },
    {
        "code": "RF06_STROKE_BEFAST",
        "title": "급성 뇌졸중 의심 (Acute Stroke - BE-FAST Positive)",
        "category": "NEUROLOGY",
        "severity": "CRITICAL_IMMEDIATE",
        "cues": ["안면마비", "구음장애", "발음이 어눌", "편마비", "한쪽 팔다리 마비", "실어증", "갑작스러운 시야장애", "갑작스러운 복시", "be-fast", "뇌졸중 의심", "hemiparesis", "dysarthria"],
        "action": "마지막 정상 확인 시각(LKW) 즉시 특정 + 손끝 혈당(BST, 저혈당 배제) + 비조영 뇌 CT(출혈 배제) 후 혈전용해술/동맥내재개통 가능 뇌졸중센터 즉시 전원 (항혈소판제 임의 투여 금지)",
        "time_target": "즉시 BST·LKW 확인 / 골든타임 전원",
    },
    {
        "code": "RF07_SEPSIS_SHOCK",
        "title": "패혈증 / 패혈성 쇼크 (Sepsis / Septic Shock - Hour-1 Bundle)",
        "category": "INFECTIOUS_CRITICAL",
        "severity": "CRITICAL_IMMEDIATE",
        "cues": ["패혈증", "패혈성 쇼크", "septic shock", "의식변화와 발열", "오한과 저혈압", "젖산 상승", "lactate 상승"],
        "action": "Surviving Sepsis 1시간 번들: ① 젖산(Lactate) 측정 ② 항생제 투여 전 혈액배양 2쌍 ③ 광범위 정주 항생제 투여 ④ 저혈압 시 정질액 30mL/kg 급속 투여 ⑤ MAP >= 65 유지를 위해 Norepinephrine 개시 및 중환자실/상급전원",
        "time_target": "1시간 이내 Sepsis Bundle 완수",
    },
    {
        "code": "RF08_RESP_FAILURE",
        "title": "급성 저산소성 호흡부전 / 중증 폐렴 (Acute Respiratory Failure)",
        "category": "PULMONARY",
        "severity": "CRITICAL_IMMEDIATE",
        "cues": ["호흡곤란", "청색증", "핑크빛 거품", "빈호흡", "산소포화도 저하", "curb-65 3", "curb-65 4", "dyspnea"],
        "action": "즉시 산소 투여(목표 SpO2 >= 94%, COPD는 88-92%), 반좌위 유지, ABGA·CXR·심전도 확인, SpO2 < 92% 또는 RR >= 30 또는 의식저하 시 기관삽관 대비 및 응급 전원",
        "time_target": "즉시 산소 공급 및 기도 확보",
    },
    {
        "code": "RF09_DVT_PE",
        "title": "심부정맥혈전증 / 급성 폐색전증 의심 (DVT / Pulmonary Embolism)",
        "category": "THROMBOEMBOLISM",
        "severity": "CRITICAL_URGENT",
        "cues": ["한쪽 다리 부종", "편측 하지 부종", "종아리 부종과 호흡곤란", "수술 후 갑작스러운 호흡곤란", "폐색전", "pulmonary embolism", "dvt 의심"],
        "action": "하지 마사지/공기압박기(IPC) 즉시 중단! 활력징후·SpO2·ECG·D-dimer 확인, 하지 도플러 초음파 또는 흉부 조영 CT(CTPA) 시행 및 금기 확인 후 항응고 요법/전원",
        "time_target": "즉시 IPC 중단 및 응급 영상 평가",
    },
    {
        "code": "RF10_ACUTE_ABDOMEN_GIBLEED",
        "title": "급성 복막염 / 위장관 출혈 / 급성 담관염 / 자궁외임신",
        "category": "GI_SURGERY",
        "severity": "CRITICAL_IMMEDIATE",
        "cues": ["반발통", "복벽 강직", "근육강직", "복막자극", "토혈", "혈변", "흑색변", "황달과 고열", "임신 중 복통", "rebound tenderness", "hematemesis", "melena"],
        "action": "즉시 금식(NPO), 굵은 말초정맥로 2개 확보 및 수액 소생, CBC/교차시험/간담도/췌장효소/가임기 hCG 확인, NSAIDs 금기, 외과/소화기응급 즉시 전원",
        "time_target": "즉시 NPO·수액소생 및 응급 전원",
    },
    {
        "code": "RF11_SPINE_INFECTION_MALIGNANCY",
        "title": "화농성 척추염 / 경막외 농양 / 척추 전이암 의심 (Infectious/Malignant Spine)",
        "category": "SPINE_INFECTION",
        "severity": "CRITICAL_URGENT",
        "cues": ["발열과 요통", "열이 나면서 허리", "오한과 허리", "시술 후 발열", "수술 후 발열과 요통", "원인불명 체중감소", "암 병력과 요통", "야간 안정시 극심한 요통", "척추염", "경막외 농양"],
        "action": "스테로이드 주사/신경차단술 절대 금지! 즉시 CBC, ESR, CRP, 혈액배양 2쌍 채취 및 조영증강 척추 MRI(Contrast MRI) 오더 (항생제 투여 전 배양 우선, 패혈증 시 즉시 투여)",
        "time_target": "즉시 스테로이드 차단 및 조영 MRI/혈액배양",
    },
    {
        "code": "RF12_ANAPHYLAXIS",
        "title": "아나필락시스 (Anaphylaxis)",
        "category": "ALLERGY_EMERGENCY",
        "severity": "CRITICAL_IMMEDIATE",
        "cues": ["아나필락시스", "주사 후 호흡곤란", "수액 후 호흡곤란", "조영제 후 두드러기", "천명음과 저혈압", "전신 두드러기와 어지러움", "후두부종", "anaphylaxis"],
        "action": "원인 약물/수액 즉시 중단! Epinephrine 0.01 mg/kg (성인 0.3~0.5 mg, 1:1000) 대퇴부 외측 근육주사(IM) 즉시 투여 (IV 단독 볼루스 금지!) + 하지 거상 + 산소 + 생리식염수 급속 정주",
        "time_target": "즉시 Epinephrine 외측 대퇴부 IM",
    },
    {
        "code": "RF13_STATUS_EPILEPTICUS",
        "title": "뇌전증 지속상태 (Status Epilepticus)",
        "category": "NEUROLOGY",
        "severity": "CRITICAL_IMMEDIATE",
        "cues": ["5분 이상 경련", "연속 경련", "의식 회복 없는 경련", "전신 경련 지속", "status epilepticus"],
        "action": "기도 확보(측와위, 억지 개구 금지) + 고농도 산소 + 즉시 혈당(BST) 확인 + Lorazepam 4mg IV 완속 투여(또는 Midazolam IM) 및 신경과/응급센터 전원",
        "time_target": "5분 이내 1차 항경련제 투여",
    },
    {
        "code": "RF14_GLYCEMIC_CRISIS",
        "title": "중증 저혈당 쇼크 / 당뇨병성 케톤산증·고삼투압 위기 (BST < 50 or > 400)",
        "category": "ENDOCRINE",
        "severity": "CRITICAL_IMMEDIATE",
        "cues": ["저혈당 쇼크", "혈당 40", "혈당 35", "bst 40", "bst < 50", "혈당 450", "혈당 500", "케톤산증", "dka", "과호흡과 고혈당"],
        "action": "BST < 50 mg/dL: 즉시 50% Dextrose 50mL IV 투여 후 15분 뒤 재측정(알코올 의존/영양결핍 시 Thiamine 100mg IV 병행). BST > 400 mg/dL: 생리식염수 수액 소생, 전해질(K+)·혈액가스·케톤 확인 및 정주 인슐린/전원",
        "time_target": "즉시 교정 및 15~60분 단위 재평가",
    },
    {
        "code": "RF15_HYPERKALEMIA",
        "title": "중증 고칼륨혈증 (K+ > 6.0 mEq/L or ECG Tent-T)",
        "category": "ELECTROLYTE_RENAL",
        "severity": "CRITICAL_IMMEDIATE",
        "cues": ["고칼륨혈증", "칼륨 6.", "칼륨 7.", "k+ 6.", "k+ 7.", "tent-t", "peaked t", "심전도 t파 상승"],
        "action": "칼륨 함유 수액(하트만/플라즈마솔루션 등)·NSAIDs·RAAS억제제 즉시 중단! 12유도 ECG 확인 + 심근막 안정화 Calcium Gluconate 10% 10-20mL IV 완속 투여 + Regular Insulin 10U + 50% DW 50mL IV + 칼륨결합제/투석 전원 검토",
        "time_target": "즉시 Calcium Gluconate IV 심근 보호",
    },
    {
        "code": "RF16_CSF_LEAK_MENINGITIS",
        "title": "척추 수술/시술 후 뇌척수액 누출 / 수막염 의심 (CSF Leak / Meningitis)",
        "category": "SPINE_POSTOP",
        "severity": "HIGH_URGENT",
        "cues": ["기립성 두통", "일어나면 두통", "수양성 배액", "맑은 진물", "뇌척수액 누출", "경막 파열", "경부 강직", "csf leak", "dural tear"],
        "action": "즉시 침상 절대 안정(Flat bed rest), 배액관 음압 해제(중력 배액 전환 또는 잠금 주치의 확인), 수분 보충·카페인 고려, 발열/경부강직 동반 시 세균성 수막염 감별 응급 조치",
        "time_target": "즉시 침상 평탄화 및 음압배액 해제 점검",
    },
    {
        "code": "RF17_THUNDERCLAP_SAH",
        "title": "벼락두통 / 지주막하출혈·뇌수막염 의심 (SNOOP10 Red Flag Headache)",
        "category": "NEUROLOGY",
        "severity": "CRITICAL_IMMEDIATE",
        "cues": ["벼락두통", "망치로 맞은 듯한 두통", "생애 최악의 두통", "갑작스러운 극심한 두통", "두통과 경부강직", "두통과 의식저하", "지주막하출혈", "thunderclap"],
        "action": "진통제만 투여 후 귀가 절대 금지! 즉시 비조영 뇌 CT + 뇌혈관 CT(CTA) 시행 및 신경외과/응급의료센터 즉시 전원(초기 CT 음성이라도 6시간 경과 시 요추천자/전원 고려)",
        "time_target": "즉시 뇌 CT/CTA 및 응급 전원",
    },
]


CLINICAL_SYNDROMES = [
    {
        "code": "SYN_LUMBAR_HIVD_RADICULOPATHY",
        "name_ko": "급성/아급성 요추 추간판 탈출증 및 신경근병증 (Lumbar HIVD with Radiculopathy)",
        "name_en": "Lumbar Herniated Intervertebral Disc with Radiculopathy",
        "specialty": "척추외과·통증의학",
        "acuity": "OUTPATIENT_OR_URGENT_BY_MOTOR",
        "positive_cues": ["방사통", "디스크", "추간판", "찌릿", "타는 듯", "작열통", "허리 숙일", "굴곡", "앉아 있", "slrt", "엄지발가락", "까치발", "l4", "l5", "s1", "다리 저림", "요통"],
        "negative_cues": ["자전거는 잘", "앉아서 쉬면 바로 호전되는 양측 종아리 파행만"],
        "must_not_miss": ["마미총 증후군(배뇨·배변장애/안장감각저하)", "화농성 척추염(발열/ESR·CRP 상승)", "혈관성 파행(말초동맥질환)", "이상근 증후군/대퇴신경병증"],
        "choi_3x3_cell": "A1×A2×B2: 척추/디스크 × 신경병성 (DRG NaV1.7 이소성 발화 + 척수후각 CaV α2δ-1 & KCC2 탈억제)",
        "pathophysiology": "섬유륜 균열로 누출된 염증성 수프(PLA2, TNF-α)가 혈관-신경 장벽이 열려 있는 DRG를 화학적으로 감작시키고 기계적 신경근 압박이 중첩됨.",
        "workup": [
            "신경학적 진찰: L4(족관절 배굴)/L5(엄지발가락 배굴 EHL)/S1(족관절 저굴) SMC Motor Grade(0~5), 피부분절 감각, SLRT 각도, 배뇨/안장감각 확인",
            "영상 검사: 요추 기립 AP/Lateral 및 굴곡·신전(Dynamic) X-ray; 중증 방사통·신경학적 결손·보존치료 불응 시 요추 MRI",
            "기본 혈액검사(약물/시술 전): CBC, Cr/eGFR(신기능 맞춤 용량), AST/ALT, 혈당, 발열 시 ESR/CRP"
        ],
        "step1_conservative": "척추 위생(요추 굴곡 전면 금지 + 맥켄지 신전 회복) + 시간약리학 약물요법(저녁 20시 Duloxetine 30mg Tmax 새벽 정렬 + 취침 전 Pregabalin 50~75mg[신기능 보정] + 위장/신장 안전 확인 후 Celecoxib 또는 대안 진통제, 2~4주)",
        "step2_interventional": "급성 극심통(VAS >= 7) 또는 2~4주 보존치료 불응 시 C-arm 유도 경추간공 신경차단술(TFESI, 횟수 기준 준수) 또는 Balloon-PEN / C-PEN 신경성형술(유착 물리 박리 + 고장성 식염수 염증 수프 세척)",
        "step3_surgical_or_transfer": "6주 이상 체계적 보존/중재 치료 실패 난치성 방사통(SNS >= 0.75) 또는 진행성 운동마비(SMC <= 3) 시 BESS 양방향 내시경 추간판절제/감압술 (마미총 증후군은 24시간 내 응급 감압)",
        "negative_gate_m0": "마비 없는 급성 디스크 탈출에서 조기 개방형 수술/나사못 유합술 금지(자연 흡수율 70~80%); 굴곡 스트레칭(무릎 가슴 당기기) 금지",
        "switching_boundary": "경과 관찰 중 EHL/족관절 근력이 Grade <= 3으로 저하되거나 잔뇨감·안장부 감각저하 발생 시 즉시 응급 MRI 및 BESS 수술 트랙으로 전환",
        "patient_metaphor": "디스크는 찢어진 피부 상처와 같고, 신경 통증은 피복 벗겨진 전선의 합선 경보입니다. 허리를 숙이는 건 반창고 붙인 상처를 매일 뜯어내는 것과 같으니 서서 세수하시고, 필요시 1mm 카테터로 염증 찌꺼기를 씻어내는 신경 대청소(PEN)로 리셋할 수 있습니다."
    },
    {
        "code": "SYN_LUMBAR_SPINAL_STENOSIS",
        "name_ko": "퇴행성 요추 척추관/추간공 협착증 및 신경인성 파행 (Lumbar Spinal Stenosis)",
        "name_en": "Degenerative Lumbar Spinal Stenosis with Neurogenic Claudication",
        "specialty": "척추외과·통증의학",
        "acuity": "OUTPATIENT_STANDARD",
        "positive_cues": ["협착증", "걸으면 다리", "보행 시", "파행", "터질 듯", "쉬면 좋아", "쪼그려 앉", "쇼핑카트", "허리 펴면", "신전 시 악화", "50m", "100m", "고령"],
        "negative_cues": ["가만히 서 있기만 해도 무관하고 걸을 때만 즉시 종아리 경련 후 서서 쉬어도 호전(혈관성 시사)"],
        "must_not_miss": ["말초동맥질환 혈관성 파행(족배동맥 맥박 소실, ABI < 0.9)", "마미총 증후군", "고관절 퇴행성 관절염/무혈성 괴사"],
        "choi_3x3_cell": "A2×C2: 척추/추간공 협착 × 신경병성·전달성 (신경근 미세허혈·정맥울혈 + DRG 만성 유착)",
        "pathophysiology": "황색인대 비후와 후관절 비대로 척추관/추간공이 좁아져 보행·기립 시 신경근 정맥 울혈 및 미세허혈성 신경인성 파행 유발.",
        "workup": [
            "이학적 검사: 연속 보행 가능 거리(m), SMC 근력, **양측 족배동맥(Dorsalis pedis)·후경골동맥 맥박 촉지 및 필요시 ABI**(혈관성 파행 필수 감별)",
            "영상 검사: 요추 기립 및 굴곡·신전(Dynamic) X-ray(>4~5mm 유동성 전방전위 확인), 요추 MRI(중심관 단면적 및 Lee 추간공 등급 평가)",
            "전신/수술전 선별: 골밀도(BMD, 노인 골다공증), eGFR/신기능, 복용 중인 항혈소판제/항응고제 확인"
        ],
        "step1_conservative": "약물치료(Limaprost[프로스타글란딘 E1 신경미세혈류 개선, 출혈위험 확인] + 저용량 Pregabalin 야간 투여 + 단기 소염진통제[신기능 정상 시]) + 실내 자전거·코어 안정화 운동",
        "step2_interventional": "보행거리 단축으로 일상 제한 시 C-arm 신경차단술 또는 Balloon-PEN(풍선확장 신경성형술로 추간공 물리적 확장 및 유착 박리)",
        "step3_surgical_or_transfer": "6~12주 비수술 치료에도 보행거리 < 100m 난치성 파행 지속 시 후관절 80% 이상 보존하는 **BESS 양방향 내시경 감압술(ULBD)** (심한 동적 불안정증이 입증된 예외에만 최소침습 유합술 검토)",
        "negative_gate_m0": "동적 불안정증이 없는 고령/골다공증 협착증 환자에게 광범위 나사못 유합술(Fusion) 시행 엄격 배제(불유합·인접분절병증 위험)",
        "switching_boundary": "보행 가능 거리 < 50m로 급감하거나 진행성 족관절 근력 약화(SMC <= 3), 배뇨장애 동반 시 BESS 내시경 감압술로 전환",
        "patient_metaphor": "신경이 지나가는 터널에 세월의 이끼(두꺼워진 인대)가 끼어 걸을 때 신경에 피가 안 통하는 상태입니다. 나사못을 박는 큰 공사 대신, 내시경으로 두꺼워진 인대만 살짝 넓혀주면 내 뼈와 근육을 그대로 지킬 수 있습니다."
    },
    {
        "code": "SYN_NOCIPLASTIC_CENTRAL_SENSITIZATION",
        "name_ko": "노시플라스틱 만성 통증 / 중추감작 / 섬유근육통·FBSS (Central Sensitization)",
        "name_en": "Nociplastic Chronic Pain / Central Sensitization / Fibromyalgia",
        "specialty": "통증의학·신경과",
        "acuity": "OUTPATIENT_STANDARD",
        "positive_cues": ["만성 요통", "3년", "수년", "전신 통증", "전신통", "수면장애", "피로", "경미한 팽윤", "검사상 정상인데", "수술 후에도 계속", "섬유근육통", "불안", "우울", "파국화", "여러 병원"],
        "negative_cues": ["명확한 단일 피부분절 급성 신경학적 마비"],
        "must_not_miss": ["류마티스 다발근통/강직성 척추염(조조강직, ESR/CRP)", "갑상선기능저하증", "잠복 우울장애/수면무호흡증", "신규 분절 신경근 압박"],
        "choi_3x3_cell": "A3×B3×C3: 중추/대뇌(DMN) × 하행억제 붕괴·노시플라스틱 (PAG-RVM NE/5-HT 고갈 + mPFC-Insula 통증 기억 고착)",
        "pathophysiology": "말초 조직 손상은 이미 치유되었거나 경미하나, 척수후각 KCC2 탈억제와 대뇌 위협 예측(Bayesian Prior)이 고착되어 경보기 센서 자체가 오작동하는 상태.",
        "workup": [
            "정밀 병력 및 척도: 통증 파국화 척도(PCS), 수면의 질, 새벽 통증 악화 여부, 기존 주사/시술 횟수 확인",
            "기질적 배제 선별검사: CBC, ESR/CRP, TSH/free T4, 비타민 D, 간·신기능 (정상 확인으로 환자 안심 근거 확보)",
            "신경학적 재검진: 새로운 국소 운동/감각 결손 부재 확인"
        ],
        "step1_conservative": "하행성 통증 억제 경로 복원 시간약리학(저녁 20시 Duloxetine 30->60mg 증량 + 취침 전 저용량 Pregabalin) + 통증 신경과학 교육(PNE, 베이즈 위협 Prior 소거) + 점진적 유산소 걷기·수면 위생 교정",
        "step2_interventional": "국소 근막 유발점(Trigger Point) 동반 시에만 제한적 TPI 또는 자율신경 안정화 보조 요법 (설명·동의 후 선택)",
        "step3_surgical_or_transfer": "수술적 치료 비적응증! 중증 우울/불안·자살사고 동반 시 정신건강의학과 협진",
        "negative_gate_m0": "반복적 스테로이드 신경차단술 남발(연간 횟수 초과), 고주파 수핵성형술 및 불필요한 척추 재수술 절대 금지 ($M=0$: 의료쇼핑 및 의인성 손상 유발)",
        "switching_boundary": "추적 중 명확한 신규 분절 방사통이나 객관적 근력 저하(SMC <= 4)가 새로 발생할 때만 국소 MRI 재평가",
        "patient_metaphor": "불은 이미 꺼졌는데 화재 경보기 센서가 예민해져서 계속 사이렌을 울리는 상태입니다. 주사로 벽을 또 뚫을 게 아니라, 저녁 약물과 걷기 운동으로 고장 난 경보기 센서를 부드럽게 리셋해야 완치됩니다."
    },
    {
        "code": "SYN_SPINAL_INFECTION",
        "name_ko": "화농성 척추염 / 경막외 농양 의심 (Pyogenic Spondylodiscitis / Epidural Abscess)",
        "name_en": "Pyogenic Spondylodiscitis / Spinal Epidural Abscess",
        "specialty": "척추외과·감염내과",
        "acuity": "EMERGENCY",
        "positive_cues": ["발열", "고열", "오한", "열이 나", "요통", "허리 통증", "시술 후", "침 맞은 후", "주사 맞은 후", "당뇨", "야간 통증", "안정 시 통증", "척추 극돌기 압통"],
        "negative_cues": [],
        "must_not_miss": ["경막외 농양에 의한 급성 척수/마미 압박", "감염성 심내막염 동반", "결핵성 척추염", "신우신염"],
        "choi_3x3_cell": "A1×A2 (감염성 염증 폭풍): 추간판 종판·경막외강 세균 증식 및 화농성 사이토카인 폭주",
        "pathophysiology": "혈행성 전파 또는 최근 침습 시술 후 추간판/척추체 종판 및 경막외강에 황색포도상구균 등이 증식하여 골파괴 및 신경 압박 초래.",
        "workup": [
            "즉시 응급 검사: CBC(백혈구 분획), ESR, CRP, Procalcitonin, **항생제 투여 전 말초 혈액배양 2쌍 이상**, 간·신기능, 혈당",
            "필수 영상: **가돌리늄 조영증강 척추 MRI (Contrast-enhanced Spine MRI)** — 경막외 농양 범위 및 신경 압박 확인",
            "원인균 규명: 신경학적 안정 및 패혈증 아닐 경우 항생제 투여 전 CT 유도 조직생검/배양 검토; 패혈증·신경마비 시 배양 채취 직후 경험적 정주 항생제 즉시 개시"
        ],
        "step1_conservative": "경구 진통제 단독 외래 귀가 불가! 입원 격리·안정 및 감염내과/척추외과 협진 하 표적 정주 항생제(예: Vancomycin + 3세대 세팔로스포린, 신기능 보정) 최소 6주 계획",
        "step2_interventional": "스테로이드 경막외 주사 절대 금기! 진단적/치료적 농양 배액술 검토",
        "step3_surgical_or_transfer": "경막외 농양으로 인한 신경학적 결손(SMC 저하), 패혈증 조절 실패, 척추 불안정 진행 시 응급 내시경/수술적 배농 및 세척술(BESS irrigation & debridement)",
        "negative_gate_m0": "감염 배제 전 스테로이드 신경차단술(TFESI/MBB) 절대 금지 ($M=0$: 농양 급속 확산 및 패혈증 유발); 패혈증 아닌 상태에서 배양 전 경구 항생제 임의 투여 지양",
        "switching_boundary": "하지 근력 저하, 배뇨장애, 혈압 저하(SBP < 90) 발생 시 즉시 응급 수술실 감압·배농 또는 상급병원 중환자 전원",
        "patient_metaphor": "단순 디스크 결림이 아니라 척추 뼈와 신경 주변에 세균 염증이 생겼을 가능성이 있어, 스테로이드 주사는 불에 기름을 붓는 격입니다. 오늘 바로 정밀 혈액배양과 조영 MRI로 원인균을 찾아 안전하게 정맥 항생제로 잡아야 합니다."
    },
    {
        "code": "SYN_VASCULAR_CLAUDICATION",
        "name_ko": "말초동맥질환 혈관성 파행 (Peripheral Arterial Disease / Vascular Claudication)",
        "name_en": "Peripheral Arterial Disease (Vascular Claudication)",
        "specialty": "혈관외과·순환기내과·척추감별",
        "acuity": "URGENT_SAME_DAY",
        "positive_cues": ["걸으면 종아리", "서서 쉬면 호전", "허리 구부려도 무관", "발이 차갑", "냉감", "족배동맥 맥박 감소", "흡연", "당뇨", "고혈압", "피부 창백", "발가락 상처"],
        "negative_cues": ["쇼핑카트 밀면 2배 더 걷는다"],
        "must_not_miss": ["급성 하지 허혈(6P: Pain, Pallor, Pulselessness, Paresthesia, Paralysis, Poikilothermia -> 응급 혈관개통)", "요추관 협착증 동반(복합 파행)", "복부 대동맥류"],
        "choi_3x3_cell": "C1: 혈관/신경 × 허혈성 침해수용성 통증 (골격근 산소 요구량 불일치)",
        "pathophysiology": "장골·대퇴·슬와동맥 죽상경화 협착으로 보행 시 하지 근육 허혈 유발; 자세(굴곡) 변화가 아니라 운동 중단만으로 수분 내 해소되는 것이 협착증과의 핵심 감별점.",
        "workup": [
            "필수 진찰: 양측 대퇴·슬와·족배·후경골동맥 맥박 비교, 모세혈관 재충혈 시간, 피부 온도·궤양 확인",
            "정량 검사: **발목-상완 혈압지수(ABI, < 0.9 진단)**, 하지 동맥 도플러 초음파 또는 하지 혈관 조영 CT(신기능 확인 후)",
            "심뇌혈관 위험인자: HbA1c, 지질프로필, Cr/eGFR, 12유도 ECG"
        ],
        "step1_conservative": "금연 필수 + 항혈소판제(Aspirin 또는 Clopidogrel) + 고강도 Statin + Cilostazol(심부전 금기 확인!) + 감독하 보행 운동",
        "step2_interventional": "일상 제한 중증 파행 또는 임계 하지 허혈(안정시 통증, 궤양, ABI < 0.4) 시 혈관내 풍선성형/스텐트 시술 의뢰",
        "step3_surgical_or_transfer": "급성 하지 허혈(맥박 완전 소실 + 창백 + 감각/운동 마비) 시 6시간 내 응급 혈전제거/우회술 가능 혈관센터 즉시 전원",
        "negative_gate_m0": "맥박/ABI 확인 없이 MRI상 경미한 협착만 보고 불필요한 척추 시술·수술 시행 금지 ($M=0$); 울혈성 심부전 환자에게 Cilostazol 투여 금기",
        "switching_boundary": "안정 시 발 통증, 발가락 청색증/괴사, 급성 냉감·맥박 소실 발생 시 즉시 응급 혈관외과 전원",
        "patient_metaphor": "다리 신경 길이 좁아진 게 아니라 다리로 피를 보내는 수도관이 좁아져 걸을 때 근육이 숨찬 상태입니다. 허리 주사가 아니라 다리 혈관 흐름 검사(ABI)와 혈관 치료가 정석입니다."
    },
    {
        "code": "SYN_ACS_CHEST_PAIN",
        "name_ko": "급성 관상동맥 증후군 / 허혈성 흉통 의심 (Suspected ACS / Angina)",
        "name_en": "Suspected Acute Coronary Syndrome / Ischemic Chest Pain",
        "specialty": "순환기내과·응급의학",
        "acuity": "EMERGENCY",
        "positive_cues": ["흉통", "가슴 통증", "명치 답답", "쥐어짜", "압박감", "식은땀", "호흡곤란", "좌측 팔", "턱 통증", "계단 오를 때 가슴", "두근거림"],
        "negative_cues": [],
        "must_not_miss": ["STEMI/NSTEMI", "급성 대동맥박리(양팔 혈압차 >20mmHg, 찢어지는 등 통증)", "급성 폐색전증", "긴장성 기흉"],
        "choi_3x3_cell": "C1 (내장성 심근 허혈 연관통): 심장 교감신경 구심성 T1-T5 척수 수렴 방사통",
        "pathophysiology": "관상동맥 죽상반 파열·혈전 또는 산소 수급 불균형으로 심근 허혈 및 괴사 위험 발생.",
        "workup": [
            "**도착 10분 이내 12유도 심전도(ECG)** (증상 지속 시 15~30분 간격 연속 측정)",
            "핵심 혈액검사: **고감도 심근효소(hs-Troponin I/T, 기저 및 1~3시간 추적)**, CBC, 전해질(K+, Mg2+), Cr/eGFR, D-dimer(폐색전/박리 의심 시)",
            "영상: 흉부 X-ray(종격동 확장·기흉·폐부종 확인, 단 전원 지연 금지!), 양측 상지 혈압 측정"
        ],
        "step1_conservative": "즉시 절대 안정, 심전도·산소포화도 연속 모니터링(SpO2 < 90% 시 산소), 정맥로 확보; 대동맥박리/출혈 배제된 전형적 ACS 의심 시 의료진 판단 하 Aspirin 300mg 씹어 복용",
        "step2_interventional": "영양수액이나 위장약 투여로 경과관찰하며 시간 지체 금지! 급성기 완전 배제 후 안정형 흉통에서만 심초음파(TTE)/관상동맥 CT 외래/입원 평가",
        "step3_surgical_or_transfer": "ST 상승, 신규 LBBB, Troponin 상승, 지속 흉통, 실신, 저혈압/부정맥 시 **즉시 119 구급차(제세동기 동승)로 PCI 가능 심혈관센터 응급 전원**",
        "negative_gate_m0": "ECG·Troponin 확인 전 '역류성 식도염/담 결림'으로 단정하여 귀가 조치 금지 ($M=0$); 대동맥박리 미배제 상태에서 항응고제 투여 금지; NSAIDs(심근경색 위험 증가) 투여 금기",
        "switching_boundary": "초기 ECG 정상이어도 흉통 재발·지속 또는 추적 Troponin 상승 시 즉시 응급 전원",
        "patient_metaphor": "가슴과 명치 통증은 위장 문제처럼 보여도 심장 혈관이 보내는 긴급 신호일 수 있습니다. 10분 안에 심전도와 심장 효소 검사부터 확인해 가장 위험한 심근경색을 먼저 막는 것이 최우선입니다."
    },
    {
        "code": "SYN_RESP_PNEUMONIA_BRONCHITIS",
        "name_ko": "급성 하기도 감염 / 지역사회획득 폐렴·급성 기관지염 (CAP / Acute Bronchitis)",
        "name_en": "Community-Acquired Pneumonia / Acute Lower Respiratory Infection",
        "specialty": "호흡기내과",
        "acuity": "OUTPATIENT_OR_INPATIENT_BY_CURB65",
        "positive_cues": ["기침", "가래", "객담", "발열", "호흡곤란", "숨이 차", "가슴 아픈 기침", "수포음", "폐렴", "기관지염"],
        "negative_cues": [],
        "must_not_miss": ["중증 패혈증/저산소성 호흡부전(SpO2 < 92%, CURB-65 >= 3)", "폐결핵(2~3주 이상 기침, 체중감소, 야간발한)", "급성 심부전/폐색전증", "폐암 폐쇄성 폐렴"],
        "choi_3x3_cell": "Systemic Organ (호흡기 폐포·기관지 염증 반응)",
        "pathophysiology": "세균 또는 호흡기 바이러스 감염으로 폐포 삼출액 축적 및 환기-관류 불균형 발생.",
        "workup": [
            "기본 필수 평가: 활력징후(호흡수 RR 필수!), **SpO2**, 청진, **CURB-65 점수(혼돈, BUN>19, RR>=30, SBP<90/DBP<=60, 65세 이상)** 산출",
            "영상 및 검사: **흉부 X-ray(CXR)**, CBC, CRP, 간·신기능(eGFR), 전해질; 고위험/입원 시 호흡기 바이러스 PCR·객담/혈액배양",
            "적응증 기반 추가: CXR 불명확·치료 3일 미호전 시 Chest CT (급성 감염기에 폐기능검사 PFT는 연기!)"
        ],
        "step1_conservative": "폐렴 확인 시 가이드라인 기반 경험적 항생제(예: 베타락탐 + 마크로라이드 또는 호흡기 퀴놀론[알레르기·QT연장·신기능 확인]) + 해열진통(아세트아미노펜 1일 최대 4g 이하, 간질환 감량) + 진해거담제; 단순 바이러스성 급성 기관지염은 불필요 항생제 지양",
        "step2_interventional": "CURB-65 2점 또는 경구 섭취 불량·고령 동반질환 시 입원 수액·정주 항생제 치료 (비급여 회복주사는 목적·한계·비용 설명 및 동의 후 선택)",
        "step3_surgical_or_transfer": "SpO2 < 92%, RR >= 30회/분, SBP < 90 mmHg, 의식저하, CURB-65 >= 3점 시 응급 산소 처치 후 중환자 치료 가능 상급병원 전원",
        "negative_gate_m0": "SAA 단독 판단 금지; 급성 폐렴/감염기에 PFT 강행 금지; 저산소증 환자에서 전원 지연하고 영양수액 먼저 투여 금지 ($M=0$)",
        "switching_boundary": "외래 치료 48~72시간 내 해열되지 않거나 호흡곤란·SpO2 < 94% 발생 시 즉시 재내원 및 Chest CT/입원 전환",
        "patient_metaphor": "기관지와 폐에 염증이 생겼을 때는 산소 수치(SpO2)와 폐 사진으로 폐렴 여부를 정확히 가르는 것이 첫걸음입니다. 숨이 가빠지거나 열이 3일 이상 지속되면 바로 다시 오셔야 합니다."
    },
    {
        "code": "SYN_ACUTE_ABDOMINAL_PAIN",
        "name_ko": "급성 복통 / 담도·췌장·위장관 염증 증후군 (Acute Abdominal Pain Syndrome)",
        "name_en": "Acute Abdominal Pain (GI / Hepatobiliary / Pancreatic / Appendiceal)",
        "specialty": "소화기내과·외과",
        "acuity": "URGENT_SAME_DAY",
        "positive_cues": ["복통", "배가 아", "우상복부", "우하복부", "명치 통증", "구토", "설사", "발열", "오심", "식후 통증", "압통"],
        "negative_cues": [],
        "must_not_miss": ["범발성 복막염/장천공(반발통·복벽강직)", "급성 충수염/급성 담낭염·담관염(Charcot 3징)", "급성 췌장염", "가임기 여성 자궁외임신(소변 hCG 필수!)", "고령 장간막 허혈 / 하벽 심근경색(명치 통증)"],
        "choi_3x3_cell": "Systemic Organ (내장성 구심 신경 및 벽측 복막 체성 통증)",
        "pathophysiology": "장관 점막 염증·폐색 또는 담석/췌장 효소 자가소화로 내장통에서 벽측 복막 자극통으로 이행 가능.",
        "workup": [
            "필수 진찰 및 기본 검사: 복부 촉진(국소 압통·반발통·Murphy 징후), CBC, CRP, LFT(AST/ALT/ALP/Bilirubin), **Amylase/Lipase**, 요검사",
            "필수 안전 선별: **가임기 여성 소변 hCG(영상 촬영 전 필수)**, 50세 이상/심혈관 위험군 상복부·명치 통증 시 **12유도 ECG**",
            "적응증 맞춤 영상: 우상복부/간담도 -> 복부 초음파; 국소 반발통·65세 이상·원인 불명 급성 복증 -> 복부 조영 CT(eGFR 및 Metformin 복용 확인)"
        ],
        "step1_conservative": "원인 감별 전 금식(NPO) 및 정질액 수액 교정 + 진경제/제토제/아세트아미노펜주 통증 조절 (외과적 복증 배제 후 경증 장염 시 경구 수분·식이 단계 재개)",
        "step2_interventional": "탈수·구토 지속 시 입원 수액 요법 및 담낭염/게실염 등 확인 시 표적 정주 항생제",
        "step3_surgical_or_transfer": "반발통·복벽강직, 토혈·혈변, 고열 동반 황달, SBP < 90 mmHg, 급성 충수염/천공/장폐색/자궁외임신 확인 시 외과·응급수술 병원 즉시 전원",
        "negative_gate_m0": "원인 미상 복통/출혈 의심 환자에게 NSAIDs(케토롤락 등) 투여 금기 ($M=0$: 위장관 천공·출혈 및 신손상 악화); 가임기 여성 hCG 미확인 CT 촬영 금지",
        "switching_boundary": "통증이 우하복부로 국소화되거나 반발통·고열·구토 악화, 흑색변/혈변 발생 시 즉시 외과 전원",
        "patient_metaphor": "배 통증은 단순 장염부터 맹장염·담낭염까지 원인이 다양해 진통제로 덮기 전에 피검사와 초음파·CT로 수술이 필요한 상태인지 먼저 안전하게 확인해야 합니다."
    },
    {
        "code": "SYN_ACUTE_NEUROPATHIC_ZOSTER_DM",
        "name_ko": "말초 신경병증성 통증 / 대상포진 후 신경통·당뇨병성 신경병증 (PHN / DPN)",
        "name_en": "Peripheral Neuropathic Pain (PHN / Diabetic Polyneuropathy)",
        "specialty": "신경과·통증의학·내과",
        "acuity": "OUTPATIENT_STANDARD",
        "positive_cues": ["대상포진", "수포", "옷깃만 스쳐도", "이질통", "allodynia", "양측 발바닥 저림", "장갑 양말", "당뇨 신경병증", "화끈거림", "전격통", "칼로 베는 듯"],
        "negative_cues": [],
        "must_not_miss": ["안부 대상포진(Hutchinson 징후 -> 각막 침범 실명 위험, 즉시 안과 협진)", "람세이헌트 증후군(안면마비+귀 수포)", "길랑-바레 증후군(급성 상행성 근력약화)", "비타민 B12 결핍/요독성 신경병증"],
        "choi_3x3_cell": "C1×C2×B2: 말초 소섬유/DRG × 신경병성 (C/A-delta 역치 저하 Allodynia + 척수후각 KCC2 탈억제)",
        "pathophysiology": "바이러스성 DRG 신경원 손상 또는 고혈당 미세혈관 손상으로 NaV1.7/1.8 과발현 및 중추 시냅스 CaV α2δ-1 과활성 유발.",
        "workup": [
            "이학적 검사: 피부분절 수포 흔적, 브러시 이질통(Allodynia) 영역, 진동각·모노필라멘트 감각, 심부건반사",
            "대사·신기능 평가: **Cr/eGFR(필수! Pregabalin/Gabapentin 및 항바이러스제 신배설 감량 기준)**, HbA1c, 비타민 B12, TSH"
        ],
        "step1_conservative": "급성 대상포진(72시간 내): 신기능 맞춤 경구 항바이러스제 + 적극적 초기 통증 차단; 신경병증 통증: **eGFR 맞춤 용량 Pregabalin 또는 Gabapentin(취침 전 시작 후 점진 증량)** ± Duloxetine 저녁 복용 + 국소 5% Lidocaine 패치(노인/신부전 환자에 전신 부작용 최소)",
        "step2_interventional": "급성 중증 대상포진 통증(PHN 이행 예방 목적) 시 조기 선택적 신경근 차단술 또는 교감신경차단술 검토",
        "step3_surgical_or_transfer": "눈 코끝 수포(안부 대상포진) 시 당일 안과 응급 의뢰; 급성 상행성 사지 위약 시 상급병원 신경과 전원",
        "negative_gate_m0": "eGFR < 30 환자에게 상용량 Pregabalin(150~300mg/d)/항바이러스제 무감량 투여 금지 ($M=0$: 의식혼미·근간대경련·급성신부전 유발); 신경병증 통증에 단독 NSAIDs 장기 처방 무효·유해",
        "switching_boundary": "어지러움·졸림·보행 비틀거림 발생 시 즉시 α2δ 리간드 감량 및 국소 패치 위주 전환; 시력 저하·안구통 발생 시 즉시 안과 전원",
        "patient_metaphor": "바이러스나 혈당 때문에 신경 전선의 피복이 벗겨져, 살갗에 옷만 스쳐도 불꽃이 튀는 상태입니다. 일반 소염진통제가 아니라 벗겨진 신경 전선을 안정시키는 전용 약을 신장 기능에 딱 맞춘 안전 용량으로 써야 합니다."
    },
    {
        "code": "SYN_DIZZINESS_VERTIGO",
        "name_ko": "어지럼증 / 말초성 현훈 vs 중추성 뇌간·소뇌 어지럼 감별 (Vertigo / Dizziness)",
        "name_en": "Acute Vestibular Syndrome / Vertigo (Peripheral vs Central)",
        "specialty": "신경과·이비인후과",
        "acuity": "URGENT_SAME_DAY",
        "positive_cues": ["어지럼", "어지러", "빙글빙글", "현훈", "회전성", "고개 돌릴 때", "구역", "구토", "안진", "보행 실조", "이석증", "전정신경염"],
        "negative_cues": [],
        "must_not_miss": ["후순환계 소뇌/뇌간 뇌경색(HINTS 양성: 정상 두부충동검사 + 방향전환 안진 + 수직 사편위, 보행 불능, 구음장애·복시)", "기립성 저혈압/부정맥 실신 전단계", "저혈당"],
        "choi_3x3_cell": "Systemic Neuro (전정-소뇌-뇌간 안구운동 네트워크)",
        "pathophysiology": "반고리관 이석 이동(BPPV)/전정신경 염증 또는 추골기저동맥 허혈에 의한 소뇌·뇌간 전정핵 손상.",
        "workup": [
            "필수 침상 신경학적 검사: **HINTS 검사(Head Impulse, Nystagmus, Test of Skew)**, 소뇌 기능(손가락-코, 발꿈치-정강이), **독립 기립·보행 가능 여부(서지 못하면 중추성 강력 의심!)**, Dix-Hallpike 검사",
            "기본 안전 검사: 활력징후(기립 혈압 포함), 손끝 혈당(BST), 12유도 ECG(부정맥 감별), 전해질·CBC",
            "뇌 영상 적응증: HINTS 중추성 소견, 고령·혈관위험인자 초발 지속 어지럼, 신경학적 징후·신규 후두부 두통 동반 시 **뇌 확산강조 MRI(Brain DWI, 비조영 CT만으로는 초기 소뇌경색 배제 불가!)**"
        ],
        "step1_conservative": "BPPV 확진 시 이석정복술(Epley/Barbecue maneuver); 급성 말초성 전정신경염 시 단기 전정억제제(1~3일 이내 제한 사용 후 조기 전정재활)",
        "step2_interventional": "심한 구토·탈수 시 정질액 수액 및 제토제 정주 (수액으로 중추성 평가 지연 금지)",
        "step3_surgical_or_transfer": "중추성 안진, 독립 보행 불능, 구음장애·복시·편측 감각이상·후두부 벼락두통 동반 시 즉시 뇌졸중센터(MRI 가능 병원) 응급 전원",
        "negative_gate_m0": "'뇌 CT 정상이니 뇌경색 아님'이라고 단정 금지 ($M=0$: 후두개와 소뇌경색 CT 민감도 < 20%); 전정억제제 장기 투여 금지(중추 보상 지연)",
        "switching_boundary": "관찰 중 복시, 딸꾹질 지속, 구음장애, 편측 실조, 두통 악화 발생 시 즉시 응급 뇌 MRI/전원",
        "patient_metaphor": "어지럼증은 귀의 평형센서 문제(이석증)가 흔하지만, 작은 뇌(소뇌) 혈관 문제와 꼭 구별해야 합니다. 눈동자 움직임과 걸음걸이 균형을 먼저 꼼꼼히 확인해 가장 위험한 뇌졸중부터 배제해 드리겠습니다."
    },
    {
        "code": "SYN_ACUTE_STROKE_TIA",
        "name_ko": "급성 허혈성 뇌졸중 / 일과성 허혈발작 의심 (Acute Stroke / TIA)",
        "name_en": "Suspected Acute Ischemic Stroke / Transient Ischemic Attack",
        "specialty": "신경과·응급의학",
        "acuity": "EMERGENCY",
        "positive_cues": ["편마비", "한쪽 팔다리 마비", "구음장애", "발음이 어눌", "안면마비", "실어증", "한쪽 감각 저하", "갑작스러운 시야장애", "일시적 마비", "be-fast"],
        "negative_cues": [],
        "must_not_miss": ["뇌내출혈/지주막하출혈(출혈 배제 전 항혈전제 금기!)", "급성 저혈당 모방(BST 즉시 확인)", "복합 편두통/경련 후 Todd 마비"],
        "choi_3x3_cell": "Supraspinal CNS: 대뇌 중대뇌동맥/추골기저동맥 허혈 반음영(Penumbra) 시간 의존 괴사",
        "pathophysiology": "뇌혈관 폐색 후 분당 190만 개의 신경세포가 소실되므로 골든타임(tPA 4.5h / 동맥내 혈전제거술 6~24h) 내 재개통이 예후를 결정함.",
        "workup": [
            "즉시 현장 확인: **마지막 정상 확인 시각(LKW)**, **손끝 혈당(BST)**, 활력징후·SpO2, NIHSS 간이 평가",
            "응급 뇌 영상: **즉시 비조영 뇌 CT(출혈 배제)** 및 뇌혈관 CT(CTA)/확산강조 MRI 가능 뇌졸중센터 연계",
            "기저 검사(전원 지연 금지!): 12유도 ECG(심방세동 확인), CBC, PT/aPTT, 전해질, 신기능"
        ],
        "step1_conservative": "기도 확보·낙상 방지, SpO2 < 94% 시 산소, 포도당 함유 수액 회피(생리식염수 유지), **허혈성 뇌졸중 초기 과도한 혈압 강하 금지**(tPA 미시행 시 220/120 미만 유지)",
        "step2_interventional": "뇌출혈 배제 전 Aspirin/Clopidogrel/항응고제 임의 투여 절대 금지!",
        "step3_surgical_or_transfer": "**즉시 119 지역 뇌졸중센터(Stroke Unit) 응급 전원** (증상이 호전된 TIA라도 48시간 내 뇌경색 재발 고위험이므로 당일 응급 전원 원칙)",
        "negative_gate_m0": "뇌 영상 출혈 배제 전 항혈소판제/혈전용해제 투여 금지 ($M=0$); 설하 니페디핀 등 급격한 혈압 강하 금지(뇌관류압 붕괴); 영양수액 투여로 전원 지체 금지",
        "switching_boundary": "이송 중 의식 수준 저하(GCS 감소) 또는 구토 발생 시 기도 흡인 방지 측와위 및 기관삽관 대비",
        "patient_metaphor": "뇌혈관이 막히면 1분 1초마다 뇌세포가 손상됩니다. 증상이 잠깐 좋아졌더라도 큰 뇌경색의 전조일 수 있어 지금 바로 뇌졸중 전문센터로 이송해 혈관을 열어야 합니다."
    },
    {
        "code": "SYN_CERVICAL_RADICULOMYELOPATHY",
        "name_ko": "경추 추간판 탈출증 / 경추 척수증 (Cervical Radiculopathy / Myelopathy)",
        "name_en": "Cervical Radiculopathy / Degenerative Cervical Myelopathy",
        "specialty": "척추외과·신경외과",
        "acuity": "URGENT_SAME_DAY",
        "positive_cues": ["목 통증", "어깨에서 손까지 저림", "젓가락질", "단추 채우기", "손이 둔", "걸음걸이가 휘청", "보행 비틀", "경추", "spurling", "hoffmann", "양손 저림"],
        "negative_cues": [],
        "must_not_miss": ["경추 척수증(젓가락질 어눌·보행장애·상위운동신경원 징후 -> 비수술 도수교정 금기!)", "회전근개 파열/손목터널증후군 중복(Double crush)", "뇌졸중/운동신경원질환(ALS)"],
        "choi_3x3_cell": "A2×C2 (경추 신경근 및 척수 백질로 압박): 피질척수로(Corticospinal tract) 및 후주 전도 장애",
        "pathophysiology": "경추 추간판 탈출·후종인대골화증(OPLL)이 신경근(방사통) 또는 중심 척수(미세수지운동 소실·강직성 보행장애)를 압박함.",
        "workup": [
            "신경학적 필수 진찰: Spurling 검사, 어깨 외전 완화 징후(Bakody sign), **Hoffmann 반사·심부건반사 항진·Tandem 일자보행·10초 주먹쥐기 검사(척수증 선별)**",
            "영상 검사: 경추 AP/Lateral(OPLL·전만 확인)/Dynamic X-ray, 척수증 징후 또는 난치성 방사통 시 **경추 MRI(T2 척수 고신호 Myelomalacia 확인)**"
        ],
        "step1_conservative": "[단순 신경근병증] 경추 중립 자세 교육(스마트폰 고개 숙임 금지) + 시간약리학 약물치료; **[경추 척수증 의심 시] 보존 지연 대신 조기 척추외과 정밀 수술 평가**",
        "step2_interventional": "척수증 없는 난치성 경추 신경근병증에서 숙련의 투시 유도 경추 신경차단술 또는 경추 PEN 신중 시행",
        "step3_surgical_or_transfer": "경추 척수증(미세운동 장애·보행실조·MRI 척수신호변화) 또는 진행성 상지 마비(SMC <= 3) 시 조기 내시경 후방 추간공감압술(BESS PCF) 또는 전방 경추유합/후방 척수성형술",
        "negative_gate_m0": "경추 척수증 또는 OPLL 환자에게 고속 경추 도수교정(Chiropractic thrust)·과신전 견인 치료 절대 금지 ($M=0$: 급성 사지마비 유발 위험!)",
        "switching_boundary": "젓가락질·글씨쓰기 악화, 다리 뻣뻣함·보행 휘청거림, 배뇨 빈뇨/절박뇨 발생 시 즉시 경추 MRI 및 수술적 감압 전환",
        "patient_metaphor": "목에서 팔로 가는 작은 가지 신경만 눌린 것인지, 온몸으로 내려가는 중심 고속도로(척수)가 눌린 것인지가 가장 중요합니다. 손놀림이 둔해지면 고속도로 압박 신호이므로 목을 꺾는 도수치료는 피하고 정밀 MRI부터 확인해야 합니다."
    },
    {
        "code": "SYN_UTI_PYELONEPHRITIS_STONE",
        "name_ko": "급성 신우신염 / 요로결석 — 비척추성 옆구리·허리 통증 (APN / Urolithiasis)",
        "name_en": "Acute Pyelonephritis / Ureterolithiasis Mimicking Low Back Pain",
        "specialty": "신장내과·비뇨의학·내과",
        "acuity": "URGENT_SAME_DAY",
        "positive_cues": ["옆구리 통증", "측복통", "늑골척추각", "cvat", "배뇨통", "빈뇨", "잔뇨감과 발열", "혈뇨", "소변이 붉", "오한과 옆구리", "신우신염", "요로결석"],
        "negative_cues": ["자세 변경 시에만 정확히 재현되는 피부분절 하지 저림"],
        "must_not_miss": ["요로폐쇄 동반 패혈성 신우신염(폐쇄성 요로패혈증 -> 응급 경피적 신루술/요관스텐트 필수!)", "복부 대동맥류 파열(고령 박동성 종괴+측복통+저혈압 -> 초음파/CT 즉시!)"],
        "choi_3x3_cell": "Visceral-Somatic Convergence (T10-L2 신장피막·요관 내장 구심성 연관 요통)",
        "pathophysiology": "상행성 세균 감염에 의한 신실질 염증 부종 또는 요관 결석 폐색 경련이 T10-L2 피부분절로 연관통을 일으켜 요추 디스크로 흔히 오인됨.",
        "workup": [
            "필수 진찰 및 소변 검사: **늑골척추각 압통(CVAT) 타진**, 요검사(농뇨·아질산염·혈뇨), **항생제 투여 전 소변배양(및 발열 시 혈액배양 2쌍)**",
            "혈액 및 영상: CBC, CRP, **Cr/eGFR(폐쇄성 급성신손상 확인)**; 결석·수신증·농양 감별을 위해 **신장/방광 초음파 또는 비조영 복부 CT**"
        ],
        "step1_conservative": "[단순 APN] 배양 채취 후 경험적 항생제(예: 3세대 세팔로스포린 정주 후 경구 전환, 신기능 맞춤) + 충분한 수액 보충 + 해열진통(Acetaminophen 우선); [단순 소형 결석] 수분 섭취 + 알파차단제(Tamsulosin) 배출 요법",
        "step2_interventional": "오심·구토·고열·고령·당뇨 동반 신우신염은 입원 정주 항생제 및 수액 치료",
        "step3_surgical_or_transfer": "**결석 폐색(수신증)이 동반된 발열성 신우신염** 또는 패혈성 쇼크 시 항생제만으로 치료 불가 -> 즉시 응급 요관스텐트/경피적 신루술(PCN) 가능 병원 비뇨의학과 전원",
        "negative_gate_m0": "옆구리·허리 통증을 단순 요통으로 오인해 척추 주사만 놓거나, 탈수/신손상 동반 신우신염·결석 환자에게 무분별한 고용량 NSAIDs 반복 투여 주의 ($M=0$)",
        "switching_boundary": "항생제 투여 48~72시간 후에도 고열 지속 또는 혈압 저하·소변량 감소 시 즉시 복부 CT 재평가(신주위 농양/폐쇄 확인) 및 전원",
        "patient_metaphor": "허리 근육이나 디스크가 아니라 콩팥이나 요관에 염증·돌이 생겨 등 쪽으로 통증이 비치는 상태입니다. 소변검사와 콩팥 영상으로 막힌 곳이 없는지 확인하는 것이 가장 안전합니다."
    },
    {
        "code": "SYN_HEADACHE_MIGRAINE_SNOOP",
        "name_ko": "급성/재발성 두통 — 일차성 편두통·긴장형 vs 이차성 위험 두통 감별 (Headache SNOOP10)",
        "name_en": "Headache Evaluation (Primary Migraine/TTH vs SNOOP10 Secondary Causes)",
        "specialty": "신경과·응급의학",
        "acuity": "URGENT_IF_RED_FLAG",
        "positive_cues": ["두통", "머리가 아", "편두통", "박동성 두통", "빛 공포", "소리 공포", "구역과 두통", "뒷목이 뻐근", "벼락두통", "생애 최악의 두통"],
        "negative_cues": [],
        "must_not_miss": ["지주막하출혈(1분 내 최고조에 달하는 벼락두통)", "세균성/바이러스성 뇌수막염(발열+경부강직)", "측두동맥염(50세 이상 신규 두통+턱 파행+시력저하, ESR 상승)", "뇌종양/뇌정맥동혈전증"],
        "choi_3x3_cell": "Trigeminovascular System (삼차신경혈관 CGRP 감작 및 중추 감각처리 이상)",
        "pathophysiology": "일차성 두통은 삼차신경절 CGRP 방출 및 뇌간 조절 이상이나, SNOOP10 위험 징후가 있을 때는 뇌출혈·수막염·종괴에 의한 뇌막 견인통을 최우선 배제해야 함.",
        "workup": [
            "필수 위험 선별(SNOOP10): 발열·체중감소(Systemic), 신경학적 결손(Neurologic), **갑작스러운 벼락 발병(Onset sudden)**, **50세 이후 초발(Older age)**, 기존 두통 양상 변화·기침/발살바 악화(Pattern change)",
            "신경학적 진찰: 의식, 동공·안저 유두부종, 뇌신경, 경부강직(Meningismus), 사지 근력·보행",
            "적응증 기반 뇌 영상: SNOOP10 양성 시 즉시 뇌 CT/CTA(급성 출혈) 또는 뇌 MRI"
        ],
        "step1_conservative": "[SNOOP10 음성 일차성 편두통] 조기 급성기 약물(Triptan[관상동맥질환·조절불량 고혈압 금기!] 또는 Acetaminophen/NSAIDs, 월 10~15일 이하 제한으로 약물과용두통 예방) + 수면·카페인·유발요인 교정",
        "step2_interventional": "월 4회 이상 빈발 편두통 시 예방약물 또는 후두신경차단술/보툴리눔독소/CGRP 표적 치료 검토",
        "step3_surgical_or_transfer": "벼락두통, 경부강직·발열, 국소 신경학적 결손, 유두부종 동반 시 즉시 응급실 뇌 CT/CTA 및 신경외과·신경과 전원",
        "negative_gate_m0": "벼락두통 환자에게 뇌 영상 확인 없이 진통제 주사만 투여 후 귀가 조치 절대 금지 ($M=0$); 급성기 진통제 주 3회 이상 장기 남용(약물과용두통 유발) 차단",
        "switching_boundary": "두통 중 복시·발음어눌·한쪽 마비·구토 분출·고열 발생 시 즉시 119 응급실 내원",
        "patient_metaphor": "두통은 흔한 편두통일 수도 있지만, 번개처럼 갑자기 시작된 두통은 뇌혈관 출혈 신호일 수 있어 위험 신호(SNOOP10) 유무부터 철저히 점검해 드립니다."
    },
    {
        "code": "SYN_PERIPHERAL_JOINT_MSK",
        "name_ko": "말초 관절 급만성 통증 — 슬관절 골관절염·회전근개 질환 vs 화농성·결정성 관절염",
        "name_en": "Peripheral Joint Disorder (OA / Rotator Cuff vs Septic / Crystal Arthritis)",
        "specialty": "정형외과·통증의학",
        "acuity": "OUTPATIENT_OR_URGENT_IF_HOT_JOINT",
        "positive_cues": ["무릎 통증", "슬관절", "계단 내려갈 때 무릎", "어깨 통증", "팔을 들어올릴", "야간 어깨 통증", "회전근개", "오십견", "관절 부종", "관절 열감"],
        "negative_cues": [],
        "must_not_miss": ["급성 화농성 관절염(단일 관절 급성 부종·열감·발열·능동/수동 가동범위 전면 제한 -> 응급 관절천자 필수, 스테로이드 주사 금기!)", "통풍/가성통풍 급성 발작", "경추 신경근병증 연관 어깨 통증"],
        "choi_3x3_cell": "B1×B2: 관절/근육 × 침해수용성(활막 염증) 및 말초 감작",
        "pathophysiology": "연골 마모·힘줄 퇴행성 파열에 의한 기계적·염증성 통증이나, 급성 열감·발열 동반 시 세균성 활막 파괴(수일 내 연골 영구 손상) 감별이 최우선임.",
        "workup": [
            "이학적 검사: 능동 vs 수동 관절가동범위(ROM), 국소 열감·삼출액(Ballottement), 회전근개(Neer/Hawkins/Empty can) 또는 반월상연골(McMurray) 검사, 경추 Spurling 감별",
            "영상 및 천자: 체중부하 기립 관절 X-ray, 정밀 초음파/MRI; **발열·급성 열감 종창 시 스테로이드 주입 전 진단적 관절액 천자(세포수·그램염색·배양·편광현미경) 우선!**"
        ],
        "step1_conservative": "체중 조절·대퇴사두근/견갑골 안정화 재활 운동 + 국소 NSAID 패치/겔(고령·CKD 1차 안전 선택!) ± 신장·위장 안전 확인된 단기 경구 진통제",
        "step2_interventional": "감염 완전 배제 후 초음파 유도 히알루론산/관절강 주사(급여기준 준수); 비급여 주사(PDRN/콜라겐 등)는 목적·한계·비용 설명 및 동의 후 선택",
        "step3_surgical_or_transfer": "화농성 관절염 의심 시 즉시 정형외과 응급 관절경 세척술; 전층 회전근개 파열 기능소실 또는 말기(K-L Grade 4) 보존 불응 관절염은 관절경/인공관절 수술 검토",
        "negative_gate_m0": "감염 배제되지 않은 급성 열감·부종 관절(Hot swollen joint)에 스테로이드 관절주사 절대 금지 ($M=0$); 동일 관절 단기간 반복 스테로이드 주사(연골 독성·힘줄 파열) 차단",
        "switching_boundary": "관절 주사 후 통증·부종·발열이 24~48시간 이후 오히려 급격히 악화될 경우 의인성 화농성 관절염 의심 즉시 내원",
        "patient_metaphor": "관절이 붓고 뜨거울 때는 단순 퇴행성 염증인지 세균 침투인지 먼저 가려내는 것이 연골을 지키는 핵심입니다. 안전한 국소 치료와 근력 재활을 기본으로 단계별로 접근합니다."
    },
]


DRUG_FORMULARY = [
    {
        "drug_name": "Pregabalin",
        "aliases": ["프레가발린", "리리카", "lyrica", "pregabalin"],
        "drug_class": "CaV alpha2-delta-1 리간드 (신경병증성 통증제)",
        "standard_dose": "성인 정상 신기능: 50~75mg PO 취침 전(HS) 시작 -> 내약성 확인 후 75mg bid (최대 300mg/day)",
        "chrono_rule": "취침 전(21~22시) 우선 투여로 야간 신경병성 발작 차단 및 서파수면 회복, 주간 어지럼 최소화",
        "egfr_30_59": "감량 필수: 총 일일용량 75~150mg/day (예: 25~50mg bid 또는 75mg HS)",
        "egfr_under_30": "엄격 감량 경고: eGFR 15~29는 25~75mg 1일 1회(qd); eGFR < 15는 25mg qd (투석 후 보충). 상용량(75mg bid 이상) 투여 시 의식저하·근간대경련 위험으로 차단!",
        "contraindications": ["프레가발린 과민증", "중증 미보정 신부전에서 상용량 투여"],
        "ddi_warnings": ["마약성 진통제(Tramadol/Oxycodone)·벤조디아제핀 병용 시 호흡억제 및 진정 상가작용 주의"],
        "elderly_pregnancy": "75세 이상 고령자 낙상·어지럼 고위험 -> 25~50mg HS 초저용량 시작 원칙; 임부 신중/수유 주의",
        "reimbursement_tier": "급여 (신경병증성 통증·척추신경근병증·섬유근육통 고시 기준 확인)"
    },
    {
        "drug_name": "Duloxetine",
        "aliases": ["둘록세틴", "심발타", "cymbalta", "duloxetine"],
        "drug_class": "SNRI (세로토닌-노르에피네프린 재흡수 억제제 / 하행 통증억제 강화)",
        "standard_dose": "30mg PO 1일 1회(저녁 식후) 1~2주 적응 후 필요시 60mg qd",
        "chrono_rule": "저녁 식후(20:00) 복용 시 6시간 뒤(새벽 02:00~04:00) 최고 혈중농도(Tmax) 도달하여 새벽 통증 피크 선제 억제 및 초기 오심 경감",
        "egfr_30_59": "저용량(30mg) 시작 및 이상반응 모니터링",
        "egfr_under_30": "금기 (CONTRAINDICATED): 중증 신장애(CrCl < 30 mL/min) 및 말기 신부전에서 투여 금기!",
        "contraindications": ["중증 신장애(eGFR < 30)", "만성 간질환/간부전", "조절되지 않는 협우각 녹내장", "MAOI 병용"],
        "ddi_warnings": ["Tramadol·SSRI·Triptan 병용 시 세로토닌 증후군(발열·근강직·빈맥) 주의", "NSAIDs·항응고제 병용 시 출혈 경향 증가 주의"],
        "elderly_pregnancy": "고령자 저나트륨혈증(SIADH) 및 기립성 저혈압 모니터링",
        "reimbursement_tier": "급여 (당뇨병성 신경병증·섬유근육통·만성 근골격계/골관절염 통증 기준 확인)"
    },
    {
        "drug_name": "Celecoxib / Systemic NSAIDs",
        "aliases": ["세레콕시브", "쎄레브렉스", "celecoxib", "아세클로페낙", "aceclofenac", "록소프로펜", "이부프로펜", "케토롤락", "nsaid", "소염진통제"],
        "drug_class": "선택적 COX-2 억제제 / 비스테로이드성 소염진통제",
        "standard_dose": "Celecoxib 200mg PO qd 또는 100mg bid (식후, 최소 유효 용량·최단 기간)",
        "chrono_rule": "조조강직·염증 피크 시 저녁 복용 유리; 위장 보호 고려",
        "egfr_30_59": "신중 투여/단기 제한 및 탈수 교정 후 신기능 추적 (가급적 회피 권고)",
        "egfr_under_30": "절대 금기 (CONTRAINDICATED): eGFR < 30 mL/min/1.73m2에서 전신 NSAIDs/COX-2 억제제 투여 시 급성 신부전·고칼륨혈증 유발로 차단!",
        "contraindications": ["중증 신부전(eGFR < 30)", "활동성 소화성 궤양/위장관 출혈", "급성 심근경색/관상동맥우회술(CABG) 전후/중증 심부전", "아스피린 천식", "임신 후기", "설폰아미드 알레르기(Celecoxib)"],
        "ddi_warnings": ["항응고제(Warfarin/NOAC)·항혈소판제·스테로이드 병용 시 위장관 출혈 급증", "ACEi/ARB + 이뇨제 병용 시 Triple Whammy 급성 신손상 위험"],
        "elderly_pregnancy": "65세 이상 고령자 위장관/신장/심혈관 위험 증가 -> PPI 병용 또는 Acetaminophen/국소 패치 우선 검토",
        "reimbursement_tier": "급여"
    },
    {
        "drug_name": "Acetaminophen",
        "aliases": ["아세트아미노펜", "타이레놀", "acetaminophen", "paracetamol", "아세트아미노펜주"],
        "drug_class": "중추성 해열진통제 (비마약성, 신장 안전 1차 대안)",
        "standard_dose": "경구 500~650mg tid / 정주(50kg 이상) 1g q6-8h, 1일 총량 절대 4g 이하(고령·간위험군 2~3g 이하)",
        "chrono_rule": "규칙적 간격 투여 시 마약성 진통제 요구량(Opioid-sparing) 20~30% 감소",
        "egfr_30_59": "용량 조절 불필요 (CKD 환자의 1차 선택 진통제)",
        "egfr_under_30": "사용 가능 (투여 간격 6~8시간 유지, NSAID 대체 안전 약물)",
        "contraindications": ["중증 간부전/급성 간염", "복합진통제 중복 복용으로 일일 4g 초과"],
        "ddi_warnings": ["울트라셋(Tramadol/Acetaminophen) 등 복합제와 성분 중복 합산량 반드시 확인", "만성 음주자 간독성 주의"],
        "elderly_pregnancy": "고령 및 임부에서 비교적 안전한 1차 해열진통제",
        "reimbursement_tier": "급여"
    },
    {
        "drug_name": "Sublingual Nifedipine",
        "aliases": ["설하 니페디핀", "니페디핀 설하", "sublingual nifedipine"],
        "drug_class": "속효성 칼슘채널차단제 (설하 투여 절대 금기 항목)",
        "standard_dose": "사용 금지 (NEVER USE SUBLINGUALLY)",
        "chrono_rule": "해당 없음",
        "egfr_30_59": "설하 투여 절대 금기",
        "egfr_under_30": "설하 투여 절대 금기",
        "contraindications": ["모든 병동/외래 고혈압 환자에서 설하 니페디핀 절대 금기 (예측 불가능한 혈압 폭락 -> 뇌경색·심근경색 유발)"],
        "ddi_warnings": ["급성 중증 고혈압은 표적 장기 손상 평가 후 경구 완속 강압제 또는 정주 Nicardipine/Labetalol 적정 사용"],
        "elderly_pregnancy": "전 연령 설하 투여 금지 (NDB 진료 프로토콜 v2.0 핵심 금기)",
        "reimbursement_tier": "금기"
    },
    {
        "drug_name": "Epinephrine (Anaphylaxis)",
        "aliases": ["에피네프린", "epinephrine"],
        "drug_class": "아드레날린성 작용제 (아나필락시스 1차 구명약)",
        "standard_dose": "아나필락시스: 0.01 mg/kg (성인 0.3~0.5 mg, 1:1000 원액) 대퇴부 전외측 근육주사(IM), 필요시 5~15분 간격 반복",
        "chrono_rule": "아나필락시스 인지 즉시 투여 (항히스타민제/스테로이드가 1차 약제를 대체할 수 없음)",
        "egfr_30_59": "구명 목적 감량 없음",
        "egfr_under_30": "구명 목적 감량 없음",
        "contraindications": ["아나필락시스 상황에서 절대적 금기 없음! 단, 심정지 아닌 환자에게 1:1000 원액 IV 단독 급속 정주 절대 금지(치명적 심실부정맥/뇌출혈)"],
        "ddi_warnings": ["베타차단제 복용 환자는 반응 저하 가능(불응 시 Glucagon 고려)"],
        "elderly_pregnancy": "전 연령 구명 최우선 외측 대퇴부 IM",
        "reimbursement_tier": "응급 급여"
    },
    {
        "drug_name": "Atropine",
        "aliases": ["아트로핀", "atropine"],
        "drug_class": "항콜린제 (증상성 서맥 1차 약제)",
        "standard_dose": "AHA/NDB 2026 개정 표준: 증상성 서맥 시 **1 mg IV** (3~5분마다 반복, 최대 총 3 mg) — 구버전 0.5mg 투여 지양!",
        "chrono_rule": "응급 즉시",
        "egfr_30_59": "응급 표준 용량 동일",
        "egfr_under_30": "응급 표준 용량 동일",
        "contraindications": ["무증상 서맥", "2도 Mobitz type II / 3도 완전방실차단에서는 효과 제한적 -> 경피 페이싱(TCP) 즉시 준비"],
        "ddi_warnings": ["항콜린성 섬망·요폐·협우각 녹내장 악화 주의"],
        "elderly_pregnancy": "고령자 투여 후 급성 요폐 및 섬망 관찰",
        "reimbursement_tier": "응급 급여"
    },
    {
        "drug_name": "Enoxaparin",
        "aliases": ["에녹사파린", "크렉산", "enoxaparin", "clexane"],
        "drug_class": "저분자량 헤파린 (LMWH, DVT/PE 예방 및 치료)",
        "standard_dose": "치료용량: 1 mg/kg SC q12h (주의: Nadroparin 85.5 IU/kg 용량 체계와 절대 혼동 금지!); 예방용량: 40mg SC qd",
        "chrono_rule": "척추 시술/카테터 거치 및 발거 전후 최소 12~24시간 휴약 간격 엄수(경막외 혈종 예방!)",
        "egfr_30_59": "출혈 징후 및 혈소판(HIT) 모니터링",
        "egfr_under_30": "감량 필수: CrCl < 30 mL/min 시 치료용량 1 mg/kg SC **q24h(1일 1회)**로 감량 또는 미분획 헤파린(UFH) 전환!",
        "contraindications": ["활동성 주출혈", "척추/경막외 혈종 의심", "헤파린 유발 혈소판감소증(HIT) 병력"],
        "ddi_warnings": ["NSAIDs·항혈소판제 병용 시 출혈 및 척추 경막외 혈종 위험 급증"],
        "elderly_pregnancy": "75세 이상 고령자 출혈 위험 증가 주의",
        "reimbursement_tier": "급여"
    },
    {
        "drug_name": "Limaprost",
        "aliases": ["리마프로스트", "오팔몬", "limaprost", "opalmon"],
        "drug_class": "경구 프로스타글란딘 E1 유도체 (요추관 협착증 신경 미세혈류 개선)",
        "standard_dose": "5 mcg PO tid",
        "chrono_rule": "식후 1일 3회 규칙 복용",
        "egfr_30_59": "사용 가능 (출혈 경향 관찰)",
        "egfr_under_30": "출혈 경향 주의 하 모니터링",
        "contraindications": ["임부 또는 임신 가능성 있는 여성(자궁수축 유발 금기!)", "활동성 출혈 환자"],
        "ddi_warnings": ["항혈소판제·항응고제·혈전용해제 병용 시 출혈 경향 증가; 척추 시술/수술 전 휴약 기간(통상 5~7일) 주치의 확인"],
        "elderly_pregnancy": "임부 절대 금기; 고령 협착증 환자 보행거리 개선 표준 약제",
        "reimbursement_tier": "급여 (후천성 요부척추관협착증 주관적 보행장해·하지저림 개선)"
    },
    {
        "drug_name": "NDB-IV Neuro-Recovery Protocol (#04 ALA + Carnitine + Mecobalamin)",
        "aliases": ["신경부종수액", "ndb-iv", "알파리포산", "티옥트산", "메코발라민", "영양수액"],
        "drug_class": "비급여 보조 정맥영양수액 (IVNT - 신경 산화스트레스 완충 보조)",
        "standard_dose": "적응증 확인 및 설명·동의 후 단독 생리식염수 베이스 완속 점적 정주",
        "chrono_rule": "공복 투여 시 알파리포산에 의한 일시적 저혈당 증상 주의 -> 식사 여부 및 혈당 확인",
        "egfr_30_59": "수액 총 용량 및 주입 속도 감량 주의",
        "egfr_under_30": "주의/회피 권고: 중증 신부전·투석·울혈성 심부전·폐부종 환자에서 불필요한 수액 부하(Volume overload) 및 전해질 이상 위험으로 제한!",
        "contraindications": ["응급 전원 대상 환자(수액으로 전원 지연 금지!)", "중증 심부전/폐부종/말기 신부전 체액과다", "고용량 비타민 C의 경우 G6PD 결핍·옥살산 신결석 금기", "성분 과민증"],
        "ddi_warnings": ["알파리포산은 인슐린/경구혈당강하제 효과 증강으로 저혈당 유발 가능; 항생제·타 주사제와 임의 혼합(Y-site) 지양"],
        "elderly_pregnancy": "고령자 심폐 용적 부하 속도 조절; 임부·수유부 비급여 영양수액 원칙적 회피",
        "reimbursement_tier": "비급여 (목적·기대효과·한계·비용 사전 설명 및 환자 동의/거부 의무기록 필수)"
    },
]


HIRA_RULES = [
    {
        "rule_code": "HIRA_JA46_SPINE_SURGERY",
        "domain": "척추수술 급여기준 (자46)",
        "requirement": "최소 6주 이상의 적극적인 보존적 치료(투약, 물리치료, 신경차단술 등) 시행 기록 및 영상-임상 일치 인과관계 의무기록 명시 필수.",
        "exception_clause": "단, 마미총 증후군(Cauda Equina Syndrome), 진행성 신경학적 결손(SMC Motor Grade <= 3), 또는 마약성 진통제에도 조절 불가능한 극심한 통증은 6주 미만 조기 수술 급여 인정(차트 첫 줄에 객관적 근력 등급 명시).",
        "risk_if_violated": "보존치료 기간 미충족 또는 근력 등급 누락 시 전액 삭감 위험"
    },
    {
        "rule_code": "HIRA_NERVE_BLOCK_CAP",
        "domain": "척추 신경차단술 급여기준",
        "requirement": "동일 부위 무분별한 반복 시술 지양, 주 1회 간격 및 기간 내 인정 횟수 상한 준수, 시술 전후 통증 변화(VAS) 및 투시 영상(C-arm image) 보관 필수.",
        "exception_clause": "노시플라스틱 만성 통증 환자에서 효과 없는 반복 주사 남발 금지.",
        "risk_if_violated": "초과 횟수 삭감 및 의인성 스테로이드 부작용(쿠싱, 감염, 혈당 상승)"
    },
    {
        "rule_code": "NDB_NONCOVERED_CONSENT",
        "domain": "비급여 시술·검사·영양수액 설명·동의 규율",
        "requirement": "PEN 신경성형술, 비급여 특수 치료재료, 영양수액(IVNT) 시행 전 반드시 ①목적 ②기대 효과 ③의학적 한계 ④대체 급여 치료 유무 ⑤비용을 설명하고 환자의 자율적 선택 동의를 서면/차트에 기록.",
        "exception_clause": "환자가 거부할 경우 거부를 존중하고 급여 대안을 안내하며 [설명 내용 + 거부 사유 + 대안 안내]를 의무기록에 남김.",
        "risk_if_violated": "설명 의무 위반 민원 및 비급여 환수 리스크"
    },
    {
        "rule_code": "NDB_LONGSTAY_COMMUNICATION",
        "domain": "장기입원 재평가 및 표현 리스크 관리",
        "requirement": "'치료 협조 안 하면 강제 퇴원' 등의 위압적 표현 절대 금지. '현재 급성기 입원 치료 유지의 의학적 필요성 재평가 및 외래/연계병원 회복 계획 설명' 프레임으로 주치의 면담 후 기록.",
        "exception_clause": "새로운 급성 내과/신경학적 악화 징후 발생 시 즉시 재평가.",
        "risk_if_violated": "진료거부/부당퇴원 민원 발생"
    },
]


def build_database(db_path: Path = DB_PATH) -> dict:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # 1. Backward-compatible medi_gemini_ontology table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS medi_gemini_ontology (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT NOT NULL,
            subject TEXT NOT NULL,
            predicate TEXT NOT NULL,
            object TEXT NOT NULL,
            clinical_relevance TEXT NOT NULL
        );
    """)
    cur.execute("DELETE FROM medi_gemini_ontology;")
    cur.executemany(
        "INSERT INTO medi_gemini_ontology (domain, subject, predicate, object, clinical_relevance) VALUES (?, ?, ?, ?, ?);",
        ONTOLOGY_TRIPLES,
    )

    # 2. Red Flag Kill-Switch table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS red_flag_killswitch (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            severity TEXT NOT NULL,
            cues_json TEXT NOT NULL,
            immediate_action TEXT NOT NULL,
            time_target TEXT NOT NULL
        );
    """)
    cur.execute("DELETE FROM red_flag_killswitch;")
    for rf in RED_FLAGS:
        cur.execute(
            """INSERT INTO red_flag_killswitch
               (code, title, category, severity, cues_json, immediate_action, time_target)
               VALUES (?, ?, ?, ?, ?, ?, ?);""",
            (
                rf["code"],
                rf["title"],
                rf["category"],
                rf["severity"],
                json.dumps(rf["cues"], ensure_ascii=False),
                rf["action"],
                rf["time_target"],
            ),
        )

    # 3. Clinical Syndromes DDx & Treatment Pathways
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clinical_syndromes_ddx (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name_ko TEXT NOT NULL,
            name_en TEXT NOT NULL,
            specialty TEXT NOT NULL,
            acuity TEXT NOT NULL,
            positive_cues_json TEXT NOT NULL,
            negative_cues_json TEXT NOT NULL,
            must_not_miss_json TEXT NOT NULL,
            choi_3x3_cell TEXT NOT NULL,
            pathophysiology TEXT NOT NULL,
            workup_json TEXT NOT NULL,
            step1_conservative TEXT NOT NULL,
            step2_interventional TEXT NOT NULL,
            step3_surgical_or_transfer TEXT NOT NULL,
            negative_gate_m0 TEXT NOT NULL,
            switching_boundary TEXT NOT NULL,
            patient_metaphor TEXT NOT NULL
        );
    """)
    cur.execute("DELETE FROM clinical_syndromes_ddx;")
    for syn in CLINICAL_SYNDROMES:
        cur.execute(
            """INSERT INTO clinical_syndromes_ddx (
                code, name_ko, name_en, specialty, acuity,
                positive_cues_json, negative_cues_json, must_not_miss_json,
                choi_3x3_cell, pathophysiology, workup_json,
                step1_conservative, step2_interventional, step3_surgical_or_transfer,
                negative_gate_m0, switching_boundary, patient_metaphor
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
            (
                syn["code"],
                syn["name_ko"],
                syn["name_en"],
                syn["specialty"],
                syn["acuity"],
                json.dumps(syn["positive_cues"], ensure_ascii=False),
                json.dumps(syn["negative_cues"], ensure_ascii=False),
                json.dumps(syn["must_not_miss"], ensure_ascii=False),
                syn["choi_3x3_cell"],
                syn["pathophysiology"],
                json.dumps(syn["workup"], ensure_ascii=False),
                syn["step1_conservative"],
                syn["step2_interventional"],
                syn["step3_surgical_or_transfer"],
                syn["negative_gate_m0"],
                syn["switching_boundary"],
                syn["patient_metaphor"],
            ),
        )

    # 4. Drug Safety Formulary
    cur.execute("""
        CREATE TABLE IF NOT EXISTS drug_safety_formulary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drug_name TEXT UNIQUE NOT NULL,
            aliases_json TEXT NOT NULL,
            drug_class TEXT NOT NULL,
            standard_dose TEXT NOT NULL,
            chrono_rule TEXT NOT NULL,
            egfr_30_59 TEXT NOT NULL,
            egfr_under_30 TEXT NOT NULL,
            contraindications_json TEXT NOT NULL,
            ddi_warnings_json TEXT NOT NULL,
            elderly_pregnancy TEXT NOT NULL,
            reimbursement_tier TEXT NOT NULL
        );
    """)
    cur.execute("DELETE FROM drug_safety_formulary;")
    for d in DRUG_FORMULARY:
        cur.execute(
            """INSERT INTO drug_safety_formulary (
                drug_name, aliases_json, drug_class, standard_dose, chrono_rule,
                egfr_30_59, egfr_under_30, contraindications_json, ddi_warnings_json,
                elderly_pregnancy, reimbursement_tier
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
            (
                d["drug_name"],
                json.dumps(d["aliases"], ensure_ascii=False),
                d["drug_class"],
                d["standard_dose"],
                d["chrono_rule"],
                d["egfr_30_59"],
                d["egfr_under_30"],
                json.dumps(d["contraindications"], ensure_ascii=False),
                json.dumps(d["ddi_warnings"], ensure_ascii=False),
                d["elderly_pregnancy"],
                d["reimbursement_tier"],
            ),
        )

    # 5. HIRA & Medical-Legal Rules
    cur.execute("""
        CREATE TABLE IF NOT EXISTS hira_reimbursement_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_code TEXT UNIQUE NOT NULL,
            domain TEXT NOT NULL,
            requirement TEXT NOT NULL,
            exception_clause TEXT NOT NULL,
            risk_if_violated TEXT NOT NULL
        );
    """)
    cur.execute("DELETE FROM hira_reimbursement_rules;")
    for hr in HIRA_RULES:
        cur.execute(
            """INSERT INTO hira_reimbursement_rules
               (rule_code, domain, requirement, exception_clause, risk_if_violated)
               VALUES (?, ?, ?, ?, ?);""",
            (hr["rule_code"], hr["domain"], hr["requirement"], hr["exception_clause"], hr["risk_if_violated"]),
        )

    # 6. Auditable Assist Loop Log
    cur.execute("""
        CREATE TABLE IF NOT EXISTS assist_loop_audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            case_preview TEXT NOT NULL,
            triage_level TEXT NOT NULL,
            top_diagnosis TEXT NOT NULL,
            loops_executed INTEGER NOT NULL,
            initial_score REAL NOT NULL,
            final_score REAL NOT NULL,
            final_loss REAL NOT NULL,
            red_flags_json TEXT NOT NULL,
            drug_blocks_json TEXT NOT NULL
        );
    """)

    conn.commit()
    stats = {
        "db_path": str(db_path),
        "medi_gemini_ontology": cur.execute("SELECT COUNT(*) FROM medi_gemini_ontology").fetchone()[0],
        "red_flag_killswitch": cur.execute("SELECT COUNT(*) FROM red_flag_killswitch").fetchone()[0],
        "clinical_syndromes_ddx": cur.execute("SELECT COUNT(*) FROM clinical_syndromes_ddx").fetchone()[0],
        "drug_safety_formulary": cur.execute("SELECT COUNT(*) FROM drug_safety_formulary").fetchone()[0],
        "hira_reimbursement_rules": cur.execute("SELECT COUNT(*) FROM hira_reimbursement_rules").fetchone()[0],
    }
    conn.close()
    return stats


if __name__ == "__main__":
    summary = build_database()
    print("✅ [Medi-Gemini v5.0] Unified Clinical Ontology DB built successfully:")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
