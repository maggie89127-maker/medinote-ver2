# 🏥 學習病歷產生器

將門診紀錄、急診紀錄或標準化病人腳本，轉換為結構化學習病歷，並提供臨床學習重點與 AI 即時問答。

---

## 功能總覽

| 功能 | 說明 |
|------|------|
| 📝 **學習病歷** | 根據輸入資料產生完整住院病歷（Chief Complaint → Plan） |
| 🔪 **內科 / 外科模式** | 內科敘述式、外科出院病摘式，一鍵切換 |
| 🎂⚧ **年齡 / 性別輸入** | 明確指定或自動推斷，影響 PI 首句、代名詞、ROS 性別篩選 |
| 🔬 **檢查結果輸入** | 直接貼入 Lab/Imaging，整合至 PI 及 PE/Impression |
| 📄 **過去出院診斷** | 可貼上過去診斷作為 Past History 主要來源 |
| 🧩 **分段卡片** | 病歷拆為 8 個獨立區塊，各自獨立顯示 |
| 📋 **一鍵複製** | 每個區塊都有複製按鈕 |
| 🔄 **單段重生 (Redo)** | 不滿意某段？只重新生成該段，其餘不動 |
| 📏📐 **精簡版 / 完整版** | Present Illness、Impression、Plan 可切換精簡或完整版本 |
| 🔴 **紅字標示** | ROS 與 PE 更動項目自動紅色字體 |
| ✳️ **ROS 異常提示** | ROS 有異常的項目以 `*` 紅字標示於值前方 |
| 💊 **抗生素 + 開始日期** | Impression 自動標註抗生素與 D1 日期 |
| 📚 **臨床學習重點** | 按需生成（節省 token），含 DDx、藥物、Guideline、EBM |
| 📖 **Evidence-Based Guideline** | 引用 IDSA/AHA/ESC/NCCN/ADA 等國際指引 |
| 🔎 **AI 自我查核** | 自動檢查病歷內部一致性與學習重點正確性 |
| 💬 **AI 問答** | 根據病歷內容即時提問，支援多輪對話 |
| 🤖 **多模型支援** | Claude / OpenAI / Gemini 三選一 |
| 🛡️ **去識別化** | 自動遮蔽姓名、身分證字號、電話號碼 |
| ⚠️ **安全提示 + 免責聲明** | 輸入區警告 + 頁尾免責聲明（含 token 費用提醒） |

---

## 安裝與執行

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 使用方式

1. 左側欄輸入 API Key
2. 左側面板填寫：

| 欄位 | 說明 |
|------|------|
| 🎂 年齡 | 整數，留空則自動推斷 |
| ⚧ 性別 | male / female / 自動推斷 |
| 📋 主要資料 | 門診紀錄 / 急診紀錄 / SP 腳本 |
| 🔬 檢查結果 | Lab, Imaging, EKG（選填） |
| 📄 過去出院診斷 | 過去出院或 ER 診斷（選填，優先作為 Past History） |
| 📝 補充資料 | 額外問診結果、病史（選填，PI 中藍字標示） |

3. 按「🩺 產生學習病歷」或「🔪 產生外科病歷」
4. 右側三個分頁：

| 分頁 | 功能 |
|------|------|
| 📝 學習病歷 | 8 段分段卡片，每段可 📋複製、🔄Redo、📏精簡版 |
| 📚 學習重點 | 按需生成（按鈕觸發），含 DDx、藥物、Guideline、EBM、AI 查核 |
| 💬 AI 問答 | 自由提問，多輪對話 |

---

## 內科 vs 外科模式差異

| 項目 | 🩺 內科模式 | 🔪 外科模式 |
|------|-----------|-----------|
| PI 風格 | 敘述式段落 | 出院病摘式（台灣外科住院醫師風格） |
| PI 首段 | 連續敘述含 underlying | underlying disease 用條列式 |
| PI 主體 | 完整敘述 | 精簡段落（主訴→症狀→否認→就醫→ER→admission） |
| Lab 描述 | 異常值列述 | 僅寫有臨床意義的異常 |
| Imaging | 詳細 findings | 一句話重點 |
| AI 角色 | 臨床教學醫師 | 外科住院醫師 |

### 外科模式 PI 範例

```
This is a 65-year-old male with underlying disease of:
 - Hypertension, under medication control
 - CKD stage 4 (eGFR 29)
 - Gout, on chronic uric acid lowering therapy

The patient suffered from acute right knee pain and swelling for 2 days. Accompanied with limited range of motion and difficulty ambulating. The patient denied fever, chest pain, or shortness of breath.

At triage, his vital signs were:
T:37.2 P:88 R:18 SBP:145 DBP:82 E:4 V:5 M:6 SPO2:98%.
Laboratory data revealed leukocytosis (WBC 14,200) with left shift, elevated CRP (12.5 mg/dL), and elevated uric acid (9.8 mg/dL). Serum creatinine was 2.1 mg/dL (baseline 1.8).
Plain film of right knee showed soft tissue swelling without fracture.

Under the impression of gouty arthritis with suspected secondary infection, he was admitted for further management.
```

---

## 病歷格式規則

### Plan 與 Impression 共用格式（純文字 · 空白 + 短橫線）

Plan 與 Impression 區塊統一使用**純文字格式**，不使用任何 Markdown 語法。

格式規則：

- 所有列點一律使用 `" - "`（空白 + 短橫線 + 空白）開頭
- 不可使用 `"- "` 直接開頭（無前導空白）
- 不可使用 `"*"`、`"•"`、`"·"` 或數字編號列表（`1. 2. 3.`）
- 每一條內容獨立一行，維持同一層級（不可有縮排或子項目）
- 換行前不加入任何空格（無行尾空白）
- 同一診斷的所有資訊以分號 `;` 分隔寫在同一行

即使 AI 模型輸出其他格式，後處理程式會自動轉換為 `" - "` 格式。

### Review of System (ROS)

異常項目以紅色 `*` 標示於值前方，例如：`fever:( *yes)`。未更動項目維持原樣：`cough:( no)`。
根據性別自動篩選項目。

### Physical Examination (PE)

異常發現以紅字標示（無 `*` 前綴）。

---

## 書寫風格規則

- 時態：病史使用過去式，現況使用現在式
- 代名詞：根據性別正確使用 he/she
- Lab：僅描述有臨床意義的異常值
- Imaging：一句話重點描述
- 禁止 AI 語氣（如 "comprehensive evaluation", "multifaceted approach"）
- 模仿台灣醫院真實住院醫師書寫風格

---

## 學習重點包含內容

- 📌 **主要診斷與臨床推理**
- 🔍 **鑑別診斷排序表** — 依機率排序，Markdown 表格呈現
- 💊 **治療藥物與劑量** — 藥名、劑量、途徑、頻率（含腎功能劑量調整）
- ⚠️ **Guideline 符合度檢查**
- 📖 **Evidence-Based Guideline 參考** — IDSA/AHA/ESC/NCCN/ADA（含年份、台灣差異）
- 🔬 **建議進一步檢查**
- ⚡ **學習重點摘要**
- 🔎 **AI 自我查核** — 病歷一致性 + 學習重點正確性

---

## 去識別化處理

| 類型 | 處理方式 |
|------|---------|
| 台灣身分證字號 | → `X000000000` |
| 手機號碼 | → `09XX-XXX-XXX` |
| 市話號碼 | → `0X-XXXX-XXXX` |
| 姓名 | → `XXX` |
| 病歷號 | → `XXXXXXXX` |

---

## 支援模型

| 模型 | 引擎 |
|------|------|
| Claude Sonnet 4 | Anthropic API（預設） |
| GPT-4o | OpenAI API |
| Gemini 2.0 Flash | Google AI |

---

## 色彩標示說明

| 標記 | 說明 |
|------|------|
| 🔴 紅色 | ROS / PE 更動項目 |
| `*` 紅色 | ROS 異常項目前方提示（例：`*yes`） |
| 🔵 藍色 | 補充資料內容（僅 Present Illness） |

---

## 部署

上傳 `app.py` + `requirements.txt` 至 GitHub → [share.streamlit.io](https://share.streamlit.io)
