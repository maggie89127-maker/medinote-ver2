import streamlit as st
import re
import html as html_lib

st.set_page_config(page_title="學習病歷產生器", page_icon="🏥", layout="wide", initial_sidebar_state="expanded")

# ══════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700;900&family=JetBrains+Mono:wght@400;500&display=swap');
:root{--pri:#1a5276;--pri-l:#2980b9;--border:#d5dde5}
.stApp{font-family:'Noto Sans TC',sans-serif}
h1,h2,h3{font-family:'Noto Sans TC',sans-serif!important;font-weight:700!important}
.header-banner{background:linear-gradient(135deg,#1a5276 0%,#2980b9 60%,#3498db 100%);padding:2rem 2.5rem;border-radius:12px;margin-bottom:1.5rem;color:#fff;position:relative;overflow:hidden}
.header-banner::before{content:'';position:absolute;top:-50%;left:-50%;width:200%;height:200%;background:radial-gradient(circle at 30% 70%,rgba(255,255,255,.06) 0%,transparent 60%)}
.header-banner h1{margin:0;font-size:1.8rem;color:#fff!important;position:relative;z-index:1}
.header-banner p{margin:.4rem 0 0;opacity:.85;font-size:.95rem;position:relative;z-index:1}
.section-label{background:var(--pri);color:#fff;display:inline-block;padding:.3rem 1rem;border-radius:6px;font-weight:500;font-size:.9rem;margin-bottom:.5rem}
.section-label-green{background:#1e8449;color:#fff;display:inline-block;padding:.3rem 1rem;border-radius:6px;font-weight:500;font-size:.9rem;margin-bottom:.5rem}
.section-label-purple{background:#6c3483;color:#fff;display:inline-block;padding:.3rem 1rem;border-radius:6px;font-weight:500;font-size:.9rem;margin-bottom:.5rem}

.note-card{background:#fdfdfe;border:1px solid var(--border);border-left:4px solid var(--pri-l);border-radius:8px;padding:1rem 1.2rem;margin:0 0 .65rem 0;font-size:.86rem;line-height:1.75;white-space:pre-wrap;font-family:'JetBrains Mono','Noto Sans TC',monospace}
.note-card .red{color:#c0392b;font-weight:600}
.note-card .blue{color:#2471a3;font-weight:600}
.nc-title{font-family:'Noto Sans TC',sans-serif;font-weight:700;font-size:.92rem;color:var(--pri);margin-bottom:.4rem;border-bottom:1px solid #e8edf1;padding-bottom:.3rem}

.variant-card{background:#f0f7ee;border:1px solid #c3ddb5;border-left:4px solid #27ae60;border-radius:8px;padding:.8rem 1.1rem;margin:0 0 .5rem 0;font-size:.84rem;line-height:1.7;white-space:pre-wrap;font-family:'JetBrains Mono','Noto Sans TC',monospace}
.variant-card .red{color:#c0392b;font-weight:600}
.variant-card .blue{color:#2471a3;font-weight:600}
.variant-label{font-size:.73rem;font-weight:700;color:#1e8449;margin-bottom:.15rem}

.chat-container{background:#f8f9fa;border:1px solid var(--border);border-radius:10px;padding:1rem;margin:.5rem 0;max-height:380px;overflow-y:auto}
.chat-msg-user{background:#2980b9;color:#fff;border-radius:12px 12px 4px 12px;padding:.6rem 1rem;margin:.5rem 0;max-width:85%;margin-left:auto;font-size:.85rem;text-align:right}
.chat-msg-ai{background:#fff;color:#2c3e50;border:1px solid #e0e0e0;border-radius:12px 12px 12px 4px;padding:.6rem 1rem;margin:.5rem 0;max-width:85%;font-size:.85rem;line-height:1.65;white-space:pre-wrap}

.stButton>button{background:linear-gradient(135deg,#1a5276,#2980b9)!important;color:#fff!important;border:none!important;border-radius:8px!important;padding:.6rem 2rem!important;font-weight:600!important;font-size:1rem!important;transition:all .2s}
.stButton>button:hover{transform:translateY(-1px);box-shadow:0 4px 15px rgba(26,82,118,.3)!important}
div[data-testid="stTextArea"] textarea{font-family:'JetBrains Mono','Noto Sans TC',monospace!important;font-size:.85rem!important;border-radius:8px!important;border:1.5px solid var(--border)!important;line-height:1.7!important}
.tips-box{background:#eef6fc;border:1px solid #bdd7ee;border-radius:8px;padding:.8rem 1rem;font-size:.83rem;color:#1a5276;line-height:1.55}
.safety-warning{background:#fef5e7;border:1px solid #f5cba7;border-left:4px solid #e67e22;border-radius:8px;padding:.7rem 1rem;font-size:.8rem;color:#7d6608;line-height:1.5;margin-bottom:.6rem}
.footer-disclaimer{background:#f9fafb;border-top:1px solid #e0e4e8;padding:1rem 2rem;margin-top:2rem;font-size:.76rem;color:#7f8c8d;line-height:1.55;text-align:center}
.stTabs [data-baseweb="tab-list"]{gap:.5rem}
.stTabs [data-baseweb="tab"]{border-radius:8px 8px 0 0;font-weight:600;font-size:.9rem}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# PROMPTS
# ══════════════════════════════════════════════════════════════

SYSTEM_PROMPT_BASE = r"""You are {role_description}.

CRITICAL LANGUAGE RULE:
The ENTIRE medical note content MUST be written in ENGLISH. Even if the user input is in Chinese, you MUST write all clinical content in English.
The ONLY Chinese allowed is the section headers themselves (e.g. "主訴 (Chief Complaint)").
This is non-negotiable.

Your task is to convert raw patient encounter information into a structured medical note.

If information is incomplete, infer and expand using reasonable general medical knowledge. Do NOT fabricate extreme or unlikely findings.

PATIENT DEMOGRAPHICS (CRITICAL):
{demographics_rule}

PRONOUN RULE: Use the correct pronoun (he/him/his or she/her) consistently throughout the entire note based on the patient's gender.

CRITICAL: The user may provide MULTIPLE blocks of information:
1. Main clinical data (ER note, OPD note, SP script)
2. Supplemental data (marked with "--- 補充資料 ---")
3. Examination results (marked with "--- 檢查結果 ---") — labs, imaging, reports
4. Past discharge/ER diagnoses (marked with "--- 過去出院診斷 ---")

You MUST incorporate ALL provided blocks into the note.
- For supplemental data: wrap content with [[...]] double brackets in Present Illness section ONLY.
- For examination results: integrate into Present Illness (ER course section) AND reflect in PE/Impression if relevant. Do NOT wrap with [[...]].
- For past diagnoses: use as PRIMARY source for Past History section. If not provided, infer from main text.

--------------------------------------------------
OUTPUT FORMAT

CRITICAL SECTION DELIMITER RULE:
Separate each section with EXACTLY this delimiter on its own line:
===SECTION===

Sections in order:
主訴 (Chief Complaint)
現在病症 (Present Illness)
過去病史 (Past History)
個人病史 (Personal History)
系統整理 (Review of System)
理學檢查 (Physical Examination)
臨床臆斷 (Impression)
處理計畫 (Plan)

Each section starts with its header on the first line, then content below.

--------------------------------------------------
主訴 (Chief Complaint)
One concise sentence: symptom + duration.

===SECTION===

現在病症 (Present Illness)
{pi_style}

===SECTION===

過去病史 (Past History)
{past_hx_rule}

===SECTION===

個人病史 (Personal History)
Allergy, Alcohol, Smoking, Betelnut. If missing, assume "denied".

===SECTION===

系統整理 (Review of System)

HIGHLIGHTING RULE (CRITICAL):
When you change a ROS item from its default value, you MUST do TWO things:
1. Wrap the changed value with **double asterisks** (for red highlighting).
2. Prepend the marker "⚠" (warning sign) immediately before the double asterisks, inside the parentheses.

The item name stays as plain text with NO asterisks or markers.

Examples:
- Default: fever:( no) → Changed: fever:( ⚠**yes**)
- Default: dizziness:( no) → Changed: dizziness:( ⚠**yes**)
- Default: visual acuity:( normal) → Changed: visual acuity:( ⚠**impaired**)
- Unchanged items stay exactly as template: cough:( no)

The pattern inside parentheses for changed items is: ( ⚠**value**)
DO NOT put any asterisks or markers before the item name. ONLY the value inside ( ) gets marked.

GENDER CHECK (CRITICAL):
{gender_ros_rule}

NUMBERED LIST format.

##Template:
1. General：
    weakness:( no), fatigue:( no), anorexia:( no), fever:( no), insomnia:( no)
2. Integument (skin, hair and nails)：
    changes in color:( no), pruritus:( no), rash:( no), hair loss:( no)
3. HEENT：
    a. Head - headache:( no), dizziness:( no), vertigo:( no)
    b. Eyes - visual acuity:( normal), color vision:( normal), corrective lenses:( no), photophobia:( no), diplopia:( no), pain:( no)
    c. Ears - pain:( no), discharge:( no), hearing loss:( no), tinnitus:( no)
    d. Nose - epistaxis:( no), discharge:( no), stuffiness:( no), sense of smell:( normal)
    e. Throat - status of teeth:( normal), gums:( normal), dentures:( no), taste:( normal), soreness:( no), hoarseness:( no), lump:( no)
4. Respiratory：cough:( no), sputum:( no), hemoptysis:( no), wheezing:( no), dyspnea:( no)
5. CV：edema:( no), chest distress:( no), chest pain:( no), palpitation:( no), intermittent claudication:( no), cold limbs:( no), cyanosis:( no)
6. GI：dysphagia:( no), nausea:( no), vomiting:( no), abdominal distress/pain:( no), change in bowel habit:( no), hematemesis:( no), melena:( no), bloody stool:( no)
7. GU：urinary frequency:( no), hesitancy:( no), urgency:( no), dribbling:( no), incontinence:( no), dysuria:( no), hematuria:( no), nocturia:( no), polyuria:( no)
8. Metabolic and endocrine：growth:( fair), development:( normal), weight change:( no), heat/cold intolerance:( no), nervousness:( no), sweating:( no), polydipsia:( no)
9. Hematotologic: anemia:( no), easy bruising or bleeding:( no), lymphadenopathy:( no), transfusions:( no)
10. Neuropsychiatry：dizziness:( no), syncope:( no), seizure:( no), speech disturbance:( no), loss of sensation:( no), paresthesia:( no), ataxia:( no), weakness or paralysis:( no), tremor:( no), anxiety:( no), depression:( no), irritability:( no)
11. Musculoskeletal：joint pain:( no), stiffness:( no), limitation of motion:( no), muscular weakness:( no), muscle wasting:( no)

===SECTION===

理學檢查 (Physical Examination)

HIGHLIGHTING RULE (CRITICAL):
ONLY mark findings that are CLINICALLY ABNORMAL and DIFFERENT from the default template.
Wrap ONLY the abnormal finding text with **double asterisks**.

Rules:
- If a finding is NORMAL or NOT SPECIFICALLY MENTIONED in the clinical data → keep the default template text as-is, with NO asterisks at all.
- If a finding is ABNORMAL based on the clinical data → change the text AND wrap it with **.
  Example: Conjunctivae: **pale** (changed from "not arrow pale")
  Example: **tenderness over RUQ**; No rebounding pain (only the changed part gets **)
- Do NOT add ** to lines that remain at their default/normal value.
- Do NOT add ** to section headers (GENERAL APPEARANCE, CHEST, etc.).

NO blank lines between PE items. Compact output.

## Template:
GENERAL APPEARANCE:
    chronic ill looking
CONSCIOUSNESS:
    Clear, E 4 V 5 M 6
HEENT:
    Sclerae: NOT icteric
    Conjunctivae: not arrow pale
    Oral cavity: Intact oral mucosa
NECK:
    Supple
    No jugular vein engorgement
CHEST:
    Breath pattern: smooth, Bilateral symmetric expansion
    No USE OF accessory muscles
    Breathing sound: bilateral clear AND symmetric breathing sound
    Wheezing: No wheezing
    Crackles: No basal crackles
HEART:
    Regular heart beat without audible murmur
    No audible S3; No audible S4
ABDOMEN:
    flat and soft, normoactive bowel sound
    No tenderness; No rebounding pain
    No muscle guarding
    No Murphy's sign
BACK:
    No knocking pain over bilateral flank area
EXTREMITIES:
    No joint deformity
    Freely movable
    No pitting edema
    Peripheral pulse: symmetric
SKIN:
    No petechiae OR ecchymosis
    No abnormal skin rash
    Skin intact
    No wound

===SECTION===

臨床臆斷 (Impression)
{imp_style}

===SECTION===

處理計畫 (Plan)
{plan_style}

--------------------------------------------------
IMPORTANT RULES
1. Read like a real hospital admission note.
2. Internal consistency across all sections.
3. If info limited, expand using common disease presentations.
4. ALL body text in English. Section headers may have Chinese.
5. No explanations. Only the note.
6. No AI filler phrases. Write like a real clinician.
7. MANDATORY: ROS changed values use ⚠ prefix followed by **value** inside parentheses (e.g. fever:( ⚠**yes**)). The ⚠ serves as an alert marker for abnormal items. PE abnormal findings use **double asterisks** only (no ⚠). Normal/unchanged items have NO asterisks.
8. MANDATORY: ===SECTION=== between every two sections.
9. MANDATORY: [[double brackets]] around supplemental-data content in Present Illness only. Do NOT use [[...]] for examination results data.
10. MANDATORY: Plan and Impression sections use PLAIN TEXT only. ALL bullet items start with " - " (space-dash-space). NO Markdown syntax, NO numbered lists, NO "*", "•", or "- " at line start. No trailing spaces before line breaks. Each item on its own line at the same level (no nesting or indentation).
11. MANDATORY: If infection is suspected, Impression MUST include antibiotics with start date: "Antibiotics: DrugA (D1: YYYY/MM/DD), DrugB (D1: YYYY/MM/DD)". Do NOT include dose. If start date not provided, use admission date.
12. MANDATORY: Use correct pronouns (he/she, him/her, his/her) throughout based on patient gender.
13. MANDATORY: Tense consistency — past tense for history and events, present tense for current status.
14. MANDATORY: Write like a real clinician in a Taiwan hospital. Avoid AI-sounding language. No phrases like "comprehensive evaluation", "multifaceted approach", "it is noteworthy that". Be direct and clinical."""

PI_FULL = r"""Narrative paragraph style for INTERNAL MEDICINE admission note.
Write like a real intern/resident in a Taiwan hospital. Use professional clinical English, NOT AI-generated language.

TENSE RULES: Use past tense for history and events. Use present tense for current status and findings.

STRUCTURE:

FIRST SENTENCE (CRITICAL):
"This is a [age]-year-old [male/female] with underlying disease of [summarized past history], who presented with [chief complaint + duration]..."

Then continue with narrative paragraphs:
- Onset, duration, characteristics (LQQOPERA — focused, no redundancy)
- Associated symptoms, pertinent negatives
- Pre-hospital course (clinic visits, prior treatment, symptom progression)

SUPPLEMENTAL DATA PLACEMENT:
If supplemental data is provided, integrate it naturally into the narrative:
- BEFORE ER course if it relates to symptom history
- AFTER symptom description if it adds clinical context
- Integrated into timeline where chronologically appropriate
Still MUST keep [[...]] marking for supplemental content.

EXAMINATION RESULTS:
If examination results (labs, imaging, reports) are provided via "--- 檢查結果 ---", integrate them into the ER course section (vital signs, labs, imaging). Do NOT wrap with [[...]].

MANDATORY LINE BREAK RULES for Present Illness:
1. When the narrative transitions to ER/hospital arrival (e.g. "At the emergency department," / "On arrival," / "Upon arrival,"), insert exactly ONE BLANK LINE before it to start a new paragraph.
2. The final sentence starting with "Under the impression of..." MUST have exactly ONE BLANK LINE before it to start a new paragraph.

ER COURSE paragraph:
- Vital signs as compact line: T:XX.X P:XX R:XX SBP:XXX DBP:XX E:X V:X M:X SPO2:XX%
- Lab: ONLY clinically significant abnormals (do not list all normal values)
- Imaging: one-sentence key findings
- ER meds: name only, no dosages

FINAL LINE: Under the impression of ..., admitted for further management.

STYLE: Write like a real clinician. No AI filler phrases. Concise and professional."""

PI_SHORT = r"""You are writing the Present Illness section as an experienced SURGICAL resident in a Taiwan hospital.
Write like a REAL surgical admission note (discharge summary style). NOT like AI-generated text.

WRITING STYLE RULES:
- Use natural, concise, professional clinical English
- Use past tense for history, present tense for current status
- Use correct pronouns (he/she) consistently
- NO AI filler phrases, NO over-explanation
- Lab: ONLY clinically significant abnormals (e.g. leukocytosis, elevated CRP, AKI)
- Imaging: ONE sentence of key findings
- Do NOT fabricate rare or unlikely findings

STRUCTURE (MUST follow this EXACT format):

PARAGRAPH 1 — Opening + underlying diseases (THIS IS THE ONLY PLACE WHERE BULLET LIST IS ALLOWED):

This is a [age]-year-old [male/female] with underlying disease of:
 - [disease 1, with relevant detail]
 - [disease 2]
 - [operation history if any]

PARAGRAPH 2 — Chief complaint + symptom narrative (CONTINUOUS PROSE, NO bullets):

The patient suffered from [chief complaint + duration]. Accompanied with [associated symptoms].
The patient denied [pertinent negatives: fever, chest pain, SOB, etc.].
[Pre-ER course: visited clinic/OPD/other hospital, treatment received, symptom progression]
He/She visited [clinic/hospital], where [treatment/advice/referral].

(INSERT ONE BLANK LINE HERE)

PARAGRAPH 3 — ER course (NEW paragraph after blank line):

At triage, his/her vital signs were:
T:XX.X P:XX R:XX SBP:XXX DBP:XX E:X V:X M:X SPO2:XX%.
Laboratory data revealed [ONLY clinically significant abnormals, described in prose].
Imaging studies showed [one-sentence key findings].
[ER interventions: drug names only, no doses]

(INSERT ONE BLANK LINE HERE)

FINAL LINE (MANDATORY, must be on its own paragraph):

Under the impression of [primary diagnosis], he/she was admitted for further management.

CRITICAL RULES:
- The underlying disease list in paragraph 1 is the ONLY place that uses " - " bullet format
- ALL other content must be continuous prose paragraphs
- Do NOT use any bullet points outside of the underlying disease list
- Examination results from "--- 檢查結果 ---" go into the ER paragraph (labs/imaging). Do NOT wrap with [[...]]
- Supplemental data from "--- 補充資料 ---" should be integrated into the symptom narrative. MUST wrap with [[...]]
- The note should look like it was written by a real surgical resident, not by AI"""

IMP_FULL = """STRICT FORMAT RULE (ABSOLUTE — NO EXCEPTIONS):
All diagnosis items MUST use PLAIN TEXT format with " - " (space-dash-space) at the start of each line.
ABSOLUTELY NO numbered lists (1. 2. 3.), NO nested lists, NO sub-items, NO indentation.
ABSOLUTELY NO "- " at line start (must have a leading space), NO "•", NO "*", NO "·".
All related info (diagnosis, differentials, antibiotics) MUST be on the SAME LINE, separated by semicolons.
Each line starts with exactly " - " (one space, one dash, one space).
No trailing spaces before line breaks.

FORMAT:
 - Primary diagnosis, r/o differentials; Antibiotics: DrugA (D1: YYYY/MM/DD), DrugB (D1: YYYY/MM/DD)
 - Other active problem (e.g. AKI, eGFR value)
 - Another active problem

CORRECT example:
 - Community-acquired pneumonia, r/o aspiration pneumonia; Antibiotics: Ceftriaxone (D1: 2025/01/15), Azithromycin (D1: 2025/01/15)
 - Acute kidney injury on CKD stage 3 (eGFR 35)
 - Hyponatremia (Na 128)

WRONG example (FORBIDDEN):
1. Community-acquired pneumonia
   - Antibiotics: Ceftriaxone

<Underlying status>
Use ONLY " - " (space-dash-space) for each item. NO blank lines between items. Compact list.
 - HTN, under medication control
 - DM type 2, on OHA
 - CKD stage 3
List all pre-existing/chronic conditions here. This stays within Impression — NOT a separate section.
If the patient has renal impairment, note it here (e.g. CKD stage X, eGFR XX)."""

IMP_SHORT = """STRICT FORMAT RULE (ABSOLUTE — NO EXCEPTIONS):
All diagnosis items MUST use " - " (space-dash-space) at the start of each line. 2-4 items max.
ABSOLUTELY NO numbered lists (1. 2. 3.), NO nested lists, NO sub-items, NO indentation.
All related info (diagnosis, differentials, antibiotics) MUST be on the SAME LINE, separated by semicolons.
No trailing spaces before line breaks.

 - Primary diagnosis with key differentials; Antibiotics: all with start date (no dose)
 - Other active problems

<Underlying status>
Use ONLY " - " (space-dash-space) for each item. NO blank lines between items.
 - condition 1
 - condition 2
This stays within Impression."""

PLAN_FULL = """FORMAT RULE (ABSOLUTE — NO EXCEPTIONS):
Every bullet item MUST start with EXACTLY one space then a dash then a space: " - " (space-dash-space).
Do NOT start any line with "- " directly (no leading space = WRONG).
Do NOT use "•", "* ", "· ", numbers, nested lists, or any other format.
The sub-section headers (Diagnostic:, Therapeutic:, Measurable goal:) are plain text with NO bullet prefix.
No nested sub-items or indentation allowed. Each item is a single flat line.

Output exactly like this:

Diagnostic:
 - Monitor renal function and electrolytes daily
 - Follow up blood culture results

Therapeutic:
 - Continue IV antibiotics
 - Fluid resuscitation with normal saline

Measurable goal:
 - Achieve afebrile status within 48 hours
 - Stabilize renal function within 5 days

Total 3-6 items. For drugs requiring renal dose adjustment, include adjustment recommendation."""

PLAN_SHORT = """FORMAT RULE (ABSOLUTE — NO EXCEPTIONS):
Every bullet item MUST start with EXACTLY " - " (space-dash-space). NO "- " at line start. NO "•", "* ", numbers, or nested lists.
Sub-section headers are plain text with NO bullet prefix.

Diagnostic:
 - item
 - item

Therapeutic:
 - item
 - item

Measurable goal:
 - item (with timeframe)

Total 3-5 items. For drugs requiring renal dose adjustment, include adjustment."""

def build_system_prompt(surgical=False, age=None, gender=None, past_hx=""):
    # Demographics rule
    if age and gender:
        demographics_rule = (
            f"The patient is a {age}-year-old {gender}.\n"
            f"The FIRST sentence of Present Illness MUST start with: "
            f'"This is a {age}-year-old {gender} with underlying disease of [summarized past history], '
            f'who presented with [chief complaint]..."\n'
            f"Use {'he/him/his' if gender == 'male' else 'she/her'} pronouns throughout."
        )
    else:
        demographics_rule = (
            "Age and gender are NOT explicitly provided. Infer from clinical data if possible.\n"
            "The FIRST sentence of Present Illness should still follow the pattern: "
            '"This is a [age]-year-old [male/female] with underlying disease of ..., who presented with ..."'
        )

    # Gender-specific ROS rule
    if gender == "male":
        gender_ros_rule = (
            "The patient is MALE.\n"
            "Do NOT include female-specific items (e.g. menstruation, pregnancy, vaginal discharge)."
        )
    elif gender == "female":
        gender_ros_rule = (
            "The patient is FEMALE.\n"
            "Do NOT include male-specific items (e.g. prostate symptoms). "
            "Add gynecological items if clinically indicated."
        )
    else:
        gender_ros_rule = (
            "Determine the patient's sex from the clinical data.\n"
            "- For MALE patients: Do NOT include female-specific items.\n"
            "- For FEMALE patients: Do NOT include male-specific items."
        )

    # Past history rule
    if past_hx.strip():
        past_hx_rule = (
            "The user has provided past discharge/ER diagnoses below. Use this as the PRIMARY source.\n"
            "Format as discharge summary style:\n"
            "- Chronic diseases\n"
            "- Previous admission diagnoses (with dates if available)\n"
            "- Operation history\n"
            "Supplement with any additional history from the main clinical data."
        )
    else:
        past_hx_rule = "List: Chronic diseases, Operation history, Previous admission history. Infer from main clinical data."

    role_desc = (
        "an experienced surgical resident and clinical teaching physician. "
        "You write admission notes in the style commonly used in Taiwan hospitals — "
        "concise, professional, discharge-summary-like. You avoid AI-sounding language "
        "and write like a real surgeon"
    ) if surgical else (
        "an experienced clinical physician and medical educator"
    )

    return SYSTEM_PROMPT_BASE.format(
        role_description=role_desc,
        pi_style=PI_SHORT if surgical else PI_FULL,
        imp_style=IMP_SHORT if surgical else IMP_FULL,
        plan_style=PLAN_SHORT if surgical else PLAN_FULL,
        demographics_rule=demographics_rule,
        gender_ros_rule=gender_ros_rule,
        past_hx_rule=past_hx_rule,
    )

LEARNING_ZONE_PROMPT = """You are a senior attending physician teaching a medical student.

Based on the following medical note, provide a clinical learning summary in Traditional Chinese (繁體中文). Use medical English terms where appropriate.

CRITICAL FORMATTING RULE: For ALL bullet-point lists, each item MUST be on its own line. Never put multiple items on the same line. Use "- " prefix for every item. This is essential for readability.

Use these exact markdown headers:

#### 📌 主要診斷與臨床推理
2-3 sentences on why this is the most likely diagnosis.

#### 🔍 鑑別診斷

Markdown table ranked by clinical likelihood:

| 排序 | 鑑別診斷 | 支持點 | 不支持點 |
|------|---------|--------|---------|
| 1 | Disease A | ... | ... |
| 2 | Disease B | ... | ... |

3-5 rows. One short sentence per cell.

#### 💊 治療原則與藥物建議
3-5 bullet points, each on its own line. Each: drug NAME, DOSE, ROUTE, FREQUENCY. Clinical rationale. Guideline reference.

RENAL DOSE ADJUSTMENT (CRITICAL): If the patient has ANY sign of renal impairment (elevated Cr, low eGFR, low CrCl, AKI, CKD), you MUST for EACH drug listed:
- State whether the drug requires renal dose adjustment (Yes/No)
- If Yes: state the patient's renal function (eGFR or CrCl value), then provide the EXACT adjusted dose with route and frequency.
  Example: "Colchicine: patient eGFR 29 → reduce to 0.3mg PO QD (standard: 0.6mg BID; per CrCl <30: halve dose and reduce frequency)"
  Example: "Teicoplanin: after loading doses, reduce maintenance to Q48H for CrCl <30"
- If No: state "no renal adjustment needed" briefly
- Always double-check the adjustment is correct per package insert or guideline

**⚠️ Guideline 符合度檢查**: Review if treatment aligns with guidelines. Flag discrepancies. Specifically check if renal-adjusted doses are correct.

#### 📖 Evidence-Based Guideline 參考
2-4 bullet points, each on its own line. Cite guideline name, organization, year.
Priority: IDSA, AHA, ACC, ESC, NCCN, ADA, GOLD, KDIGO, Surviving Sepsis Campaign.
If Taiwan differs: "台灣臨床實務差異：..."
If evidence limited: "Evidence is limited; practice may vary depending on institution."

#### 🔬 建議進一步檢查
3-5 bullet points, each on its own line, with clinical rationale.

#### ⚡ 學習重點摘要
3-5 high-yield pearls, each on its own line. Add a comparison table if useful.

#### 🔎 AI 自我查核

Part A — 病歷查核:
Review the medical note and check:
- Internal inconsistencies (e.g. ROS says no fever but PE shows T:39)
- Missing critical information
- Clinically implausible findings
- Impression vs Present Illness/PE consistency
- Plan vs Impression coverage

Part B — 學習重點查核:
Also review YOUR OWN learning content above and check:
- Are the differential diagnoses clinically reasonable for this presentation?
- Are the drug dosages correct per current guidelines?
- Are the cited guidelines accurate (correct organization, correct year, correct recommendation)?
- Are the suggested workup items appropriate and not excessive?
- Do the learning pearls contain any inaccurate or misleading statements?

Format as checklist, each item on its own line:
- ✅ or ⚠️ for each
- If all consistent: "✅ 本病歷及學習重點內容一致，未發現明顯矛盾或錯誤。"
- If issues found: list with ⚠️ and briefly explain

Rules:
- 繁體中文 for explanations, English for medical terms.
- Standard adult dosing from current guidelines.
- No AI filler. Write like a real attending.
- EVERY bullet point must be on its own line. No inline lists."""

CHAT_SYSTEM_PROMPT = """You are a senior attending physician answering questions about this patient case.
Answer based on the note. If not in note, say so and offer clinical reasoning.
Be concise. Use the student's language (繁體中文 or English). No AI filler.

===== MEDICAL NOTE =====
{note}
==========================="""

VARIANT_PROMPT = """You are an experienced clinical physician.

Rewrite this section as a SHORT/CONCISE version: keep only essential information, remove redundancy, aim for 40-60% of original length.

RULES:
- Output ONLY the rewritten content (no headers, no delimiters).
- English only. Clinically accurate.
- For Plan: each bullet MUST start with " - " (space-dash-space). NO "- " at line start. Sub-section headers (Diagnostic:, Therapeutic:, Measurable goal:) are plain text. No nested lists.
- For Impression: ALL items use " - " (space-dash-space) format. NO numbered lists (1. 2. 3.). NO nested sub-items or indentation. All info (diagnosis, differentials, antibiotics) on the SAME line separated by semicolons. <Underlying status> uses " - " (space-dash-space) bullets with no blank lines.
- For ROS: numbered list, ⚠**value** pattern on changed items (⚠ before the **bold** value).
- For PE: no blank lines, **asterisks** on changed items.
- Preserve [[double bracket]] markers if present.
- Write like a real clinician.

===== FULL NOTE (context) =====
{full_note}
====================================

SECTION: {section_title}
ORIGINAL:
{original_content}

Write the concise version:"""

# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════

def hl(text):
    """Highlight markers → colored spans. HTML-escaped first."""
    escaped = html_lib.escape(text)
    # ⚠**value** → red, displayed as (*value) for ROS abnormal items
    escaped = re.sub(r'⚠\*\*(.+?)\*\*', r'<span class="red">*\1</span>', escaped)
    # **value** → red (PE abnormal findings)
    escaped = re.sub(r'\*\*(.+?)\*\*', r'<span class="red">\1</span>', escaped)
    # [[text]] → blue (supplemental data in PI)
    escaped = re.sub(r'\[\[(.+?)\]\]', r'<span class="blue">\1</span>', escaped)
    return escaped

def hl_plain(text):
    """Highlight markers → colored spans, then wrap each line in <div> to
    prevent Streamlit's Markdown engine from interpreting '- ' as list items
    or '<...>' as HTML tags. Produces compact, pure-text rendering."""
    escaped = html_lib.escape(text)
    escaped = re.sub(r'⚠\*\*(.+?)\*\*', r'<span class="red">*\1</span>', escaped)
    escaped = re.sub(r'\*\*(.+?)\*\*', r'<span class="red">\1</span>', escaped)
    escaped = re.sub(r'\[\[(.+?)\]\]', r'<span class="blue">\1</span>', escaped)
    lines = escaped.split('\n')
    parts = []
    for ln in lines:
        stripped = ln.strip()
        if stripped == '':
            # Preserve blank lines as a slim spacer (half-line height)
            parts.append('<div style="height:.45em"></div>')
        else:
            parts.append(f'<div style="margin:0;padding:0;line-height:1.75">{ln}</div>')
    return ''.join(parts)

def anonymize(text):
    text = re.sub(r'[A-Z][12]\d{8}', 'X000000000', text)
    text = re.sub(r'09\d{2}[\-]?\d{3}[\-]?\d{3}', '09XX-XXX-XXX', text)
    text = re.sub(r'0\d[\-]?\d{4}[\-]?\d{4}', '0X-XXXX-XXXX', text)
    text = re.sub(r'(姓名|病患|患者|個案|名字)\s*[：:]\s*\S{2,5}', r'\1：XXX', text)
    text = re.sub(r'(病歷號|Chart No|chart no|病歷號碼)\s*[：:.]\s*\S+', r'\1：XXXXXXXX', text)
    return text

def parse_sections(raw):
    parts = re.split(r'\n*===SECTION===\n*', raw)
    out = []
    for p in parts:
        p = p.strip()
        if not p: continue
        lines = p.split('\n', 1)
        out.append((lines[0].strip(), lines[1].strip() if len(lines) > 1 else ""))
    return out

def detect_provider(ka, ko, kg):
    if ka: return "Claude (Anthropic)", ka
    if ko: return "OpenAI", ko
    if kg: return "Gemini (Google)", kg
    return None, None

def call_llm(provider, key, system, user_msg, max_tokens=4096):
    if provider == "Claude (Anthropic)":
        import anthropic
        c = anthropic.Anthropic(api_key=key)
        r = c.messages.create(model="claude-sonnet-4-20250514", max_tokens=max_tokens, system=system,
                              messages=[{"role": "user", "content": user_msg}])
        return r.content[0].text
    elif provider == "OpenAI":
        from openai import OpenAI
        c = OpenAI(api_key=key)
        r = c.chat.completions.create(model="gpt-4o", max_tokens=max_tokens,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user_msg}])
        return r.choices[0].message.content
    elif provider == "Gemini (Google)":
        import google.generativeai as genai
        genai.configure(api_key=key)
        m = genai.GenerativeModel("gemini-2.0-flash")
        r = m.generate_content(f"[System]\n{system}\n\n[User]\n{user_msg}",
            generation_config=genai.types.GenerationConfig(max_output_tokens=max_tokens))
        return r.text
    raise ValueError(f"Unknown: {provider}")

def call_llm_multi(provider, key, system, messages, max_tokens=1024):
    if provider == "Claude (Anthropic)":
        import anthropic
        c = anthropic.Anthropic(api_key=key)
        r = c.messages.create(model="claude-sonnet-4-20250514", max_tokens=max_tokens, system=system, messages=messages)
        return r.content[0].text
    elif provider == "OpenAI":
        from openai import OpenAI
        c = OpenAI(api_key=key)
        r = c.chat.completions.create(model="gpt-4o", max_tokens=max_tokens,
            messages=[{"role": "system", "content": system}] + messages)
        return r.choices[0].message.content
    elif provider == "Gemini (Google)":
        import google.generativeai as genai
        genai.configure(api_key=key)
        m = genai.GenerativeModel("gemini-2.0-flash")
        conv = f"[System]\n{system}\n\n"
        for msg in messages:
            conv += f"[{'User' if msg['role'] == 'user' else 'Assistant'}]\n{msg['content']}\n\n"
        r = m.generate_content(conv, generation_config=genai.types.GenerationConfig(max_output_tokens=max_tokens))
        return r.text
    raise ValueError(f"Unknown: {provider}")

def normalize_bullets(text, section_title=""):
    """Post-process bullet formatting.
    Plan: ensure Diagnostic/Therapeutic/Measurable goal sub-items use '- '.
    Impression: FLATTEN nested sub-items into parent numbered line (semicolon join);
                ensure <Underlying status> uses '- ' with no blank lines."""
    lines = text.split('\n')
    out = []
    in_plan_subsection = False
    in_underlying = False

    for line in lines:
        stripped = line.strip()

        # ── Plan sub-section handling ──
        if "Plan" in section_title:
            if re.match(r'^(Diagnostic|Therapeutic|Measurable\s+goal)\s*:', stripped, re.IGNORECASE):
                in_plan_subsection = True
                out.append(stripped)
                continue
            if in_plan_subsection:
                if not stripped:
                    out.append(line)
                    continue
                # Already correct " - " format
                if line.startswith(' - '):
                    out.append(line)
                    continue
                # Strip any existing bullet prefix and re-format as " - "
                # Match: "- text", "* text", "• text", "· text", "– text"
                m = re.match(r'^[\s]*[-•\*·–]\s*(.*)', stripped)
                if m:
                    out.append(' - ' + m.group(1))
                    continue
                # Match: numbered items "1. text", "2) text"
                m2 = re.match(r'^[\d]+[.)]\s*(.*)', stripped)
                if m2:
                    out.append(' - ' + m2.group(1))
                    continue
                # New sub-section header → reset
                if re.match(r'^(Diagnostic|Therapeutic|Measurable\s+goal)\s*:', stripped, re.IGNORECASE):
                    out.append(stripped)
                    continue
                # Plain text line → convert to " - "
                out.append(' - ' + stripped)
                continue

        # ── Impression handling ──
        if "Impression" in section_title:
            # Detect <Underlying status> boundary
            if '<Underlying status>' in stripped or '&lt;Underlying status&gt;' in stripped or 'Underlying status' in stripped:
                in_underlying = True
                out.append(stripped)
                continue

            if in_underlying:
                # Inside Underlying status: force " - " bullets, no blank lines
                if not stripped:
                    continue
                if line.startswith(' - '):
                    out.append(line)
                    continue
                # Strip "- " at start (no leading space)
                if stripped.startswith('- '):
                    out.append(' - ' + stripped[2:])
                    continue
                m = re.match(r'^[\s]*[•\*·–]\s*(.*)', stripped)
                if m:
                    out.append(' - ' + m.group(1))
                    continue
                m2 = re.match(r'^[\d]+[.)]\s*(.*)', stripped)
                if m2:
                    out.append(' - ' + m2.group(1))
                    continue
                out.append(' - ' + stripped)
                continue
            else:
                # Before Underlying status: convert ALL items to " - " format
                # Already correct " - " format
                if line.startswith(' - '):
                    out.append(line)
                    continue
                # Numbered line (1. text) → convert to " - text"
                m_num = re.match(r'^\d+[.)]\s*(.*)', stripped)
                if m_num:
                    out.append(' - ' + m_num.group(1))
                    continue
                # "- text" at line start (no leading space) → convert
                if stripped.startswith('- '):
                    out.append(' - ' + stripped[2:])
                    continue
                # Indented or bullet sub-item → merge onto previous " - " line
                is_sub = False
                sub_content = stripped
                m_sub = re.match(r'^[\s]*[-•\*·–]\s*(.*)', stripped)
                if m_sub:
                    is_sub = True
                    sub_content = m_sub.group(1)
                elif line != line.lstrip() and stripped:
                    is_sub = True
                    sub_content = stripped

                if is_sub and out:
                    for j in range(len(out) - 1, -1, -1):
                        if out[j].startswith(' - '):
                            out[j] = out[j].rstrip() + '; ' + sub_content
                            break
                    continue

                # Blank lines → keep
                if not stripped:
                    out.append(line)
                    continue

                out.append(line)
                continue

        # ── General bullet normalization ──
        m = re.match(r'^[\s]*[•\*·–]\s*(.*)', stripped)
        if m:
            out.append(' - ' + m.group(1))
        else:
            out.append(line)

    # Remove blank lines between consecutive bullet lines (compact bullets)
    result = []
    for i, line in enumerate(out):
        if line.strip() == '' and i > 0 and i < len(out) - 1:
            prev_bullet = out[i-1].strip().startswith('- ') or out[i-1].startswith(' - ')
            next_bullet = out[i+1].strip().startswith('- ') or out[i+1].startswith(' - ')
            if prev_bullet and next_bullet:
                continue
        result.append(line)
    # Strip trailing spaces from each line
    result = [l.rstrip() for l in result]
    return '\n'.join(result)

def render_card(idx, title, body):
    """Render a clean section card."""
    if body:
        # Normalize bullets for Plan and Impression
        if "Plan" in title or "Impression" in title:
            body = normalize_bullets(body, section_title=title)
    # Use hl_plain for Plan/Impression to prevent Markdown interpretation
    if body and ("Plan" in title or "Impression" in title):
        hi_body = hl_plain(body)
    else:
        hi_body = hl(body) if body else ""
    st.markdown(f'<div class="note-card">'
                f'<div class="nc-title">{html_lib.escape(title)}</div>'
                f'{hi_body}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════
st.markdown("""<div class="header-banner">
<h1>🏥 學習病歷產生器</h1>
<p>貼入病患資訊（門診紀錄 / 急診紀錄 / 標準化病人腳本），自動產生結構化學習病歷 · 學習重點 · AI 問答</p>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🔑 API Key（輸入任一即可）")
    st.caption("優先順序：Anthropic → OpenAI → Gemini")
    ka = st.text_input("Anthropic API Key", type="password", key="ka")
    ko = st.text_input("OpenAI API Key", type="password", key="ko")
    kg = st.text_input("Gemini API Key", type="password", key="kg")
    provider, active_key = detect_provider(ka, ko, kg)
    if provider:
        st.success(f"✅ 使用：{provider}", icon="🤖")
    else:
        st.info("請輸入至少一組 API Key")
    st.markdown("---")
    st.markdown('<div style="font-size:.76rem;color:#95a5a6;line-height:1.4">'
                '📝 分段病歷｜📏 精簡版｜📚 學習重點＋EBM｜💬 AI問答｜🛡️ 去識別化<br>'
                '🔴 ROS/PE更動紅字｜* ROS異常提示｜🔵 補充資料藍字</div>', unsafe_allow_html=True)

# ── Session State ───────────────────────────────────────────
for _k, _v in [("result", ""), ("learning", ""), ("chat_history", []), ("sections_data", []), ("variants", {})]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ══════════════════════════════════════════════════════════════
# LAYOUT
# ══════════════════════════════════════════════════════════════
col_in, col_out = st.columns([2, 3], gap="large")

with col_in:
    st.markdown('<div class="section-label">📋 貼入病患資料</div>', unsafe_allow_html=True)
    st.markdown("""<div class="safety-warning">
⚠️ <b>請勿輸入可識別之病人個資</b>（姓名、身分證字號、電話等）<br>
⚠️ <b>本工具僅供教學用途</b>，不可用於真實臨床決策</div>""", unsafe_allow_html=True)

    # ── Age & Gender ──
    ag1, ag2 = st.columns(2)
    with ag1:
        patient_age = st.number_input("🎂 年齡", min_value=0, max_value=150, value=None,
                                       step=1, placeholder="e.g. 65", help="留空則由 AI 從資料推斷")
    with ag2:
        patient_gender = st.selectbox("⚧ 性別", options=["（自動推斷）", "male", "female"], index=0)

    patient_data = st.text_area("主要資料", height=220,
        placeholder="貼入門診紀錄 / 急診紀錄 / SP 腳本...", label_visibility="collapsed")

    exam_results = st.text_area("🔬 檢查結果（選填）", height=90,
        placeholder="Lab data, imaging reports, EKG findings, pathology results...",
        label_visibility="visible")

    past_hx_input = st.text_area("📄 過去出院診斷 / ER 診斷（選填）", height=90,
        placeholder="可貼上過去出院診斷、ER 診斷紀錄，作為 Past History 主要來源...",
        label_visibility="visible")

    supplement = st.text_area("📝 補充資料（選填）", height=90,
        placeholder="後續問診結果、額外病史等（中英文皆可）...",
        label_visibility="visible")

    st.markdown("""<div class="tips-box">
💡 主要＋補充資料合併生成。🔴 ROS/PE更動<span style="color:#c0392b;font-weight:700;">紅字</span>。<span style="color:#c0392b;font-weight:700;">*</span> ROS異常項目前方提示。
🔵 補充資料在PI中以<span style="color:#2471a3;font-weight:700;">藍字</span>標示。🛡️ 自動去識別化。</div>""",
                unsafe_allow_html=True)

    btn1, btn2 = st.columns(2)
    with btn1:
        gen_med = st.button("🩺 產生學習病歷", use_container_width=True)
    with btn2:
        gen_surg = st.button("🔪 產生外科病歷", use_container_width=True)

    if gen_med or gen_surg:
        surgical = gen_surg
        if not active_key:
            st.warning("請先輸入至少一組 API Key。")
        elif not patient_data.strip():
            st.error("請貼入病患資料。")
        else:
            st.session_state.update({"result": "", "learning": "", "chat_history": [], "sections_data": [], "variants": {}})
            combined = anonymize(patient_data.strip())
            if exam_results.strip():
                combined += "\n\n--- 檢查結果 ---\n" + anonymize(exam_results.strip())
            if past_hx_input.strip():
                combined += "\n\n--- 過去出院診斷 ---\n" + anonymize(past_hx_input.strip())
            if supplement.strip():
                combined += "\n\n--- 補充資料 ---\n" + anonymize(supplement.strip())

            gender_val = patient_gender if patient_gender != "（自動推斷）" else None
            sys_prompt = build_system_prompt(
                surgical=surgical,
                age=patient_age,
                gender=gender_val,
                past_hx=past_hx_input.strip(),
            )
            label = "外科" if surgical else "內科"

            with st.spinner(f"使用 {provider} 生成{label}病歷⋯"):
                try:
                    st.session_state["result"] = call_llm(provider, active_key, sys_prompt, combined)
                except Exception as e:
                    st.error(f"錯誤：{e}")

            if st.session_state["result"]:
                st.rerun()

# ── RIGHT ───────────────────────────────────────────────────
with col_out:
    if st.session_state["result"]:
        tab_note, tab_learn, tab_chat = st.tabs(["📝 學習病歷", "📚 學習重點", "💬 AI 問答"])

        with tab_note:
            result = st.session_state["result"]
            # Clean download text
            clean_dl = re.sub(r'⚠\*\*(.+?)\*\*', r'*\1', result)  # ROS abnormal → *value
            clean_dl = re.sub(r'\*\*(.+?)\*\*', r'\1', clean_dl)
            clean_dl = re.sub(r'\[\[(.+?)\]\]', r'\1', clean_dl)
            clean_dl = clean_dl.replace("===SECTION===", "").strip()
            # Normalize Plan/Impression bullet format in download text
            dl_sections = parse_sections(result)
            if dl_sections:
                for _t, _b in dl_sections:
                    if ("Plan" in _t or "Impression" in _t) and _b:
                        normalized_b = normalize_bullets(_b, section_title=_t)
                        # Also clean markers for download
                        clean_b = re.sub(r'⚠\*\*(.+?)\*\*', r'*\1', _b)
                        clean_b = re.sub(r'\*\*(.+?)\*\*', r'\1', clean_b)
                        clean_nb = re.sub(r'⚠\*\*(.+?)\*\*', r'*\1', normalized_b)
                        clean_nb = re.sub(r'\*\*(.+?)\*\*', r'\1', clean_nb)
                        if clean_b in clean_dl:
                            clean_dl = clean_dl.replace(clean_b, clean_nb)
            # Strip trailing spaces from each line in download
            clean_dl = '\n'.join(l.rstrip() for l in clean_dl.split('\n'))
            st.download_button("📥 下載完整病歷 (.txt)", data=clean_dl,
                               file_name="medical_note.txt", mime="text/plain", use_container_width=True)
            st.markdown('<div style="font-size:.74rem;color:#95a5a6;margin-bottom:.3rem">'
                        '🔴 紅色=ROS/PE更動 ｜ *=ROS異常提示 ｜ 🔵 藍色=補充資料內容 ｜ 📏=精簡版（PI·Imp·Plan）</div>',
                        unsafe_allow_html=True)

            if not st.session_state["sections_data"]:
                st.session_state["sections_data"] = parse_sections(result)
            sections = st.session_state["sections_data"]
            VARIANT_OK = {"現在病症 (Present Illness)", "臨床臆斷 (Impression)", "處理計畫 (Plan)"}

            if not sections:
                st.markdown(f'<div class="note-card">{hl(result)}</div>', unsafe_allow_html=True)
            else:
                for idx, (title, body) in enumerate(sections):
                    render_card(idx, title, body)

                    if title in VARIANT_OK:
                        if st.button("📏 精簡版", key=f"sh_{idx}"):
                            if active_key:
                                with st.spinner("生成精簡版⋯"):
                                    try:
                                        p = VARIANT_PROMPT.format(full_note=result,
                                                                  section_title=title, original_content=body)
                                        t = call_llm(provider, active_key, "", p, max_tokens=2048)
                                        v = dict(st.session_state["variants"])
                                        v.setdefault(idx, {})["short"] = t.strip()
                                        st.session_state["variants"] = v
                                    except Exception as e:
                                        st.error(str(e))
                                st.rerun()

                    sv = st.session_state["variants"].get(idx, {})
                    if "short" in sv:
                        short_body = sv["short"]
                        if "Plan" in title or "Impression" in title:
                            short_body = normalize_bullets(short_body, section_title=title)
                            short_html = hl_plain(short_body)
                        else:
                            short_html = hl(short_body)
                        st.markdown(f'<div class="variant-label">📏 精簡版</div>'
                                    f'<div class="variant-card">{short_html}</div>',
                                    unsafe_allow_html=True)

        with tab_learn:
            st.markdown('<div class="section-label-green">📚 臨床學習重點</div>', unsafe_allow_html=True)
            if st.session_state["learning"]:
                st.download_button("📥 下載學習重點 (.txt)",
                                   data=st.session_state["learning"],
                                   file_name="learning_notes.txt", mime="text/plain",
                                   use_container_width=True)
                st.markdown(st.session_state["learning"])
            else:
                st.info("按下方按鈕生成學習重點（需額外 API token）。")
                if st.button("📚 生成學習重點", use_container_width=True, key="gen_learn"):
                    if active_key:
                        with st.spinner("生成學習重點⋯"):
                            try:
                                st.session_state["learning"] = call_llm(
                                    provider, active_key, LEARNING_ZONE_PROMPT,
                                    st.session_state["result"], max_tokens=3500)
                            except Exception:
                                st.session_state["learning"] = "（生成失敗，請重試）"
                        st.rerun()
                    else:
                        st.warning("請先輸入 API Key。")

        with tab_chat:
            st.markdown('<div class="section-label-purple">💬 病歷 AI 問答</div>', unsafe_allow_html=True)
            st.caption("例如：「病患有無發燒？」「為什麼選這個抗生素？」")
            if st.session_state["chat_history"]:
                parts = []
                for m in st.session_state["chat_history"]:
                    esc = html_lib.escape(m["content"])
                    cls = "chat-msg-user" if m["role"] == "user" else "chat-msg-ai"
                    parts.append(f'<div class="{cls}">{esc}</div>')
                st.markdown(f'<div class="chat-container">{"".join(parts)}</div>', unsafe_allow_html=True)

            ci = st.text_input("提問", placeholder="輸入問題⋯", key="ci", label_visibility="collapsed")
            c1, c2 = st.columns([3, 1])
            with c1:
                send = st.button("送出", use_container_width=True, key="send")
            with c2:
                if st.button("清除", use_container_width=True, key="clr"):
                    st.session_state["chat_history"] = []
                    st.rerun()
            if send and ci.strip() and active_key:
                st.session_state["chat_history"].append({"role": "user", "content": ci.strip()})
                sys = CHAT_SYSTEM_PROMPT.format(note=st.session_state["result"])
                msgs = [{"role": m["role"], "content": m["content"]} for m in st.session_state["chat_history"]]
                with st.spinner("⋯"):
                    try:
                        ans = call_llm_multi(provider, active_key, sys, msgs)
                        st.session_state["chat_history"].append({"role": "assistant", "content": ans})
                    except Exception as e:
                        st.session_state["chat_history"].append({"role": "assistant", "content": f"錯誤：{e}"})
                st.rerun()
    else:
        st.markdown("""<div style="border:2px dashed #d5dde5;border-radius:12px;padding:4rem 2rem;text-align:center;color:#95a5a6">
<div style="font-size:3rem;margin-bottom:.5rem">📄</div>
<div>產生的學習病歷將顯示在此處</div>
<div style="font-size:.85rem;margin-top:.3rem">請先在左側貼入資料並按下按鈕</div></div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════
st.markdown("""<div class="footer-disclaimer">
⚠️ <b>免責聲明</b><br>
本工具僅供醫學教育與學習用途，不應用於實際臨床診療決策。使用者需自行判斷其正確性。<br>
使用第三方 AI API（Anthropic / OpenAI / Google），使用者需自行負責 API token 消耗與相關費用。</div>""", unsafe_allow_html=True)
