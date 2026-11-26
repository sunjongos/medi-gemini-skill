# 🕸️ [MOC] Medi-Gemini v6.0 LLM-Wiki & Neurosymbolic Ontology Map

> **Core Formula**: `Medi-Gemini = JEV Medical Router × Clinical Deep Twin × 0-Dependency Ontology`

## 1. 7대 Med-Gemini 특화 역량 노드 (`[[Med-Gemini Capabilities]]`)
- `[[WIKI-MG-01_Uncertainty_Guided_Search]]`: 샤논 엔트로피 $H(Y\mid X) \ge 0.85$ 감지 시 온도 보정($T=1.25$) 및 표적 PubMed/Cochrane/HIRA 검색 쿼리·실시간 Search Grounding 자동 실행 (`jev_medical_routes: MG_ROUTE_02_DDX_UGS`)
- `[[WIKI-MG-02_Long_Context_EHR_Needle_and_FHIR]]`: 장문 종단 의무기록에서 숨은 약물 알레르기(설파제-Celecoxib 교차반응 등), 연속 `eGFR` 급감, 잠복 출혈(`Hb` 하락) 바늘 포착 및 **HL7 FHIR R4 Bundle** 자동 합성 (`MG_ROUTE_03_LONG_EHR`)
- `[[WIKI-MG-03_Multimodal_2D_Vision_Xray_ECG_Derm]]`: 척추 기립/굴곡신전 X-ray(`Cobb`, `PI-LL`, 동적 전방전위 $\ge 4\text{mm}$), 흉부 `CXR`, 12유도 `ECG`(`ST 상승`, 고칼륨혈증 `Tent-T`, `QTc`), 화상/피부 병변 판독 (`MG_ROUTE_04_VISION_2D`)
- `[[WIKI-MG-04_Volumetric_3D_CT_3T_MRI]]`: `Pfirrmann`, `Modic Type 1~3`, `Lee Stenosis Grade 0~3`, 경추 척수 `T2 Myelomalacia`, 수술 후 경막외 혈종(`POSEH`) 및 **영상-증상 불일치(Discordance) 감사** (`MG_ROUTE_05_VISION_3D`)
- `[[WIKI-MG-05_Pharmacogenomics_CPIC_Firewall]]`: `CYP2C19`(Clopidogrel), `CYP2D6`(Codeine/Tramadol), `CYP2C9`(Celecoxib/Warfarin), `HLA-B*58:01`(Allopurinol 중증피부반응 절대금기), `HLA-B*15:02`(Carbamazepine 금기), `G6PD`(고용량 비타민C IVNT 용혈 금기) (`MG_ROUTE_06_GENOMICS_PGX`)
- `[[WIKI-MG-06_AMIE_VOI_Dialogue_and_Metaphors]]`: 기대 정보이득($\text{VOI}$) 기반 능동 문진 및 5세 눈높이 공포(Prior) 소거 비유 (`MG_ROUTE_07_AMIE_DIALOGUE`)
- `[[WIKI-MG-07_Emergency_17_Red_Flags_and_NEWS2]]`: 골든타임 응급 킬스위치 최우선 라우팅 (`MG_ROUTE_01_EMERGENCY_TRIAGE`)

## 2. 최선종 대표원장 Clinical Deep Twin 암묵지 규칙 (`:TacitRule`)
- `[[TACIT_01_MRI_DISCORDANCE]]` — *Causes* ➔ 과잉 수술·반복 주사 차단($M=0$) & 베이즈 위협 Prior 인지 재구성($M=1$)
- `[[TACIT_02_YOUNG_LARGE_DISC_ABSORPTION]]` — *Causes* ➔ 마비 없는 거대 수핵 탈출 시 대식세포 자연 흡수 유도 & `Balloon-PEN` 염증 세척
- `[[TACIT_03_ELDERLY_STENOSIS_NO_FUSION]]` — *Causes* ➔ 고령·골다공증 단순 협착에서 나사못 유합술 배제($M=0$) & `BESS` 내시경 부분감압($M=1$)
- `[[TACIT_04_CHRONOPHARMACOLOGY_03AM]]` — *Causes* ➔ 저녁 20시 `Duloxetine`($T_{\max}$ 새벽 3~4시 정렬) + 취침 전 `Pregabalin` 서파수면 복원
- `[[TACIT_05_RENAL_ANTICOAG_IMMUNE_GATE]]` — *Causes* ➔ `eGFR < 30` NSAID/Duloxetine 하드 블록 및 시술 전 항혈전제 휴약 검증
- `[[TACIT_06_UNCERTAINTY_HUMILITY_GATE]]` — *Causes* ➔ 찰리 멍거 `TOO TOUGH` 바구니 분류 후 `VOI` 최우선 검사 및 담당 전문의 결단 게이트 이관
