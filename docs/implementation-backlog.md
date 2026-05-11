# My-Agent Implementation Backlog

本文件將 `my-agent/` 專案的現有架構，整理成可實作、可排序、可追蹤的工程任務清單，目標是先完成 Claude Code 版本，再逐步擴充成支援 API key agent 與多模型供應商切換的架構。[cite:65][cite:72][cite:95][cite:96]

## 目標架構

目前的目標架構如下，核心原則是將 Discord I/O、runtime、memory 與 knowledge 分層，降低供應商耦合，並為後續 provider abstraction 預留空間。[cite:81][cite:83][cite:96]

```text
my-agent/
├── CLAUDE.md
├── bot/
│   └── discord_bot.py
├── knowledge/
│   ├── RAG.py
│   └── graph.py
├── memory/
│   ├── conversations.db
│   └── memory_store.py
├── runtime/
│   ├── claude_client.py
│   ├── tool_adapter.py
│   └── session_manager.py
└── config.py
```

## Backlog 使用方式

這份 implementation backlog 的用途，是把抽象架構翻譯成實作任務，讓開發者可以清楚知道先做什麼、依賴什麼、做到什麼算完成。[cite:106][cite:109][cite:115]

建議將此文件保留在 repo 內，例如 `docs/implementation-backlog.md`，作為總覽；實際執行時，再把每個項目拆成 GitHub Issues 或專案看板卡片，以利追蹤進度與分工。[cite:106][cite:118][cite:119]

## Phase 1：完成現有 Claude Code 架構

此階段的目標是建立一個可工作的 baseline：Discord 能接訊息，Claude Code 能驅動推理，RAG 與 graph 能作為外部能力被呼叫，記憶資料能落地保存。[cite:65][cite:72][cite:70]

### 1.1 專案與設定基礎

- [ ] 建立 `CLAUDE.md`，定義專案結構、工具說明、可改動範圍、RAG/graph 使用規則、memory policy、回覆風格與限制。[cite:66][cite:68]
- [ ] 完成 `config.py`，集中管理路徑、資料庫位置、模型名稱、timeout、回合上限與其他 runtime 設定。[cite:90][cite:91]
- [ ] 建立 `.env.example` 草稿，即使此階段尚未完全啟用多 provider，也先保留設定欄位。[cite:90][cite:97][cite:100]
- [ ] 補 `requirements.txt` 或相應依賴管理檔，明確列出 Discord、SQLite、Claude SDK 與資料處理依賴。[cite:102]

### 1.2 Discord 入口層

- [ ] 完成 `bot/discord_bot.py` 的基本事件監聽與訊息收發流程。[cite:30]
- [ ] 將 Discord 訊息、附件、使用者 ID、channel ID 轉成內部 request 結構，不在這一層做推理決策。[cite:30][cite:81]
- [ ] 建立錯誤回應與最小可用 fallback，例如 Claude runtime 異常時能回覆失敗訊息。[cite:70][cite:102]
- [ ] 定義附件進入後的前處理規則，例如純文字、PDF、URL 或其他類型如何傳入 knowledge/memory 流程。[cite:70][cite:73]

### 1.3 Claude Runtime

- [ ] 完成 `runtime/claude_client.py`，封裝 Claude Code SDK 呼叫。[cite:65][cite:72]
- [ ] 對外暴露中性方法，例如 `run_turn()`、`respond()` 或 `invoke_agent()`，避免上層直接碰 Claude SDK 細節。[cite:80][cite:81]
- [ ] 建立 Claude runtime 的錯誤處理，涵蓋 timeout、tool 呼叫失敗、回傳格式異常與 session 失效。[cite:75][cite:96]
- [ ] 確認 Claude runtime 與 `CLAUDE.md` 的責任邊界；規則說明放文件，強制保證放程式碼。[cite:69][cite:75]

### 1.4 Tool 與 Knowledge 整合

- [ ] 完成 `runtime/tool_adapter.py`，定義內部工具格式與 Claude 工具格式的對應。[cite:75][cite:96]
- [ ] 統一工具回傳格式，例如 `ok / data / error / metadata`，避免上層處理各種不一致結果。[cite:96][cite:102]
- [ ] 將 `knowledge/RAG.py` 封裝成穩定入口，例如查詢與更新函式。[cite:73][cite:75]
- [ ] 將 `knowledge/graph.py` 封裝成穩定入口，例如搜尋與寫入函式。[cite:73]
- [ ] 設計工具 allowlist 與 write-tool 保護，避免 Claude 在未限制狀態下誤寫資料。[cite:75][cite:96]

### 1.5 Session 與記憶

- [ ] 完成 `runtime/session_manager.py`，管理 session id、channel 對應、回合上限、逾時與上下文摘要。[cite:70][cite:77]
- [ ] 完成 `memory/memory_store.py`，提供 `save_message()`、`load_history()`、`save_summary()`、`search_memory()` 等介面。[cite:67][cite:70]
- [ ] 建立 `memory/conversations.db` schema，區分 raw message、summary、可檢索記憶與 metadata。[cite:67][cite:70]
- [ ] 規劃何時寫入長期記憶，避免每句對話都直接進入長期層造成雜訊。[cite:70][cite:73]

### 1.6 Phase 1 驗收

- [ ] Discord 收到訊息後，可以透過 Claude Code 正常回應。[cite:65][cite:72]
- [ ] Claude 可成功呼叫至少一個 RAG 工具與一個 graph 工具。[cite:75]
- [ ] 對話可持久化到 SQLite，重新啟動後仍能載入基礎歷史。[cite:67][cite:70]
- [ ] 主要異常情境有 fallback，包含 timeout、tool failure、空結果與格式錯誤。[cite:96][cite:102]

## Phase 2：新增 API key Agent 呼叫

此階段的目標是增加第二種 backend，讓系統除了 Claude Code SDK 之外，也能透過 API key 模式驅動 agent，並盡量不改動 bot、memory 與 knowledge 層。[cite:81][cite:83][cite:95]

### 2.1 Backend 擴充

- [ ] 在 `runtime/` 新增 API key backend，例如 `anthropic_api_client.py` 或 `provider_backends/anthropic.py`。[cite:81]
- [ ] 讓 Claude Code backend 與 API key backend 共用同一組輸入輸出介面。[cite:80][cite:81]
- [ ] 明確區分 SDK session 模式與 API 請求模式的差異，避免 session 狀態耦合在特定 provider 裡。[cite:65][cite:77]

### 2.2 通用 Schema

- [ ] 定義內部通用 schema：`AgentRequest`、`AgentResponse`、`ToolSpec`、`ToolCall`、`ToolResult`。[cite:96][cite:102]
- [ ] 將 `discord_bot.py` 改為只依賴內部 schema，不直接依賴 Claude 原生格式。[cite:81][cite:83]
- [ ] 將 `memory_store.py` 與 `session_manager.py` 改為依賴內部 schema，不依賴任一 provider 的 message structure。[cite:77][cite:81]

### 2.3 驗證與相容性

- [ ] 驗證同一筆請求在 Claude Code backend 與 API key backend 上能得到一致可接受的結果。[cite:81][cite:95]
- [ ] 驗證工具呼叫流程在兩種 backend 下都成立。[cite:75][cite:96]
- [ ] 驗證 API key 錯誤情況，如授權失敗、rate limit、模型不存在、請求超時。[cite:87][cite:96]

## Phase 3：抽象化與 `.env` 控制 Provider / Model

此階段的目標是把 provider 與 model 變成設定，而不是程式碼中的硬編碼常數，讓系統可以透過 `.env` 切換 OpenAI、Claude、Ollama 等推論來源。[cite:90][cite:95][cite:101][cite:104]

### 3.1 設定治理

- [ ] 在 `.env` 中加入 `LLM_PROVIDER`、`LLM_MODEL`、各家 API key、base URL、timeout、預設溫度等欄位。[cite:90][cite:91][cite:104]
- [ ] 建立 `.env.example` 作為團隊共用範本，避免把真實密鑰提交進版控。[cite:94][cite:97][cite:100]
- [ ] 在 `config.py` 統一讀取與驗證設定，將缺漏設定在啟動時直接報錯。[cite:91][cite:94]

### 3.2 Provider Factory

- [ ] 新增 backend factory，例如 `get_agent_backend()`，依 `LLM_PROVIDER` 回傳對應 runtime backend。[cite:96][cite:101]
- [ ] 將 provider-specific tool mapping 與 provider-specific request mapping 收斂在 runtime 層，不外溢到 bot 或 knowledge 層。[cite:81][cite:96]
- [ ] 規劃 `OLLAMA_BASE_URL` 與 open-model 設定，讓本地或自建模型服務也能納入同一抽象層。[cite:52][cite:104]

### 3.3 模型切換與路由

- [ ] 支援不同 provider 下的模型切換，例如 Claude、OpenAI、Gemini、Ollama 模型名。[cite:95][cite:101]
- [ ] 規劃模型路由策略，例如快速回覆用輕量模型、工具推理用較強模型、摘要用低成本模型。[cite:95][cite:98]
- [ ] 建立 provider health check 與 fallback 邏輯，當主模型失敗時切換備援模型。[cite:95][cite:98]

## 延伸項目

以下項目可在前三階段完成後逐步導入，以提升穩定性、可觀測性與可維護性。[cite:70][cite:95][cite:98]

- [ ] 成本與 token 使用量紀錄，支援 provider 比較與模型選型。[cite:95]
- [ ] Provider 與 tool 的可觀測性，例如請求延遲、錯誤率、tool 成功率。[cite:96]
- [ ] 記憶分層：raw conversation、summary memory、retrieval memory 分開管理。[cite:70]
- [ ] 工具權限系統，區分 read-only、write、admin 類工具。[cite:96]
- [ ] 自動摘要與對話壓縮，避免 session 過長導致上下文膨脹。[cite:70][cite:77]
- [ ] Contract tests，驗證每個 backend 都遵守相同輸入輸出介面。[cite:81][cite:102]
- [ ] 災難復原與啟動自檢，例如 DB schema 檢查、provider config 檢查、RAG 路徑檢查。[cite:91][cite:102]

## 優先順序建議

建議採用「先穩、再擴、後抽象」的順序，先建立 Claude Code baseline，再新增 API key backend，最後做 provider abstraction 與多模型切換；這樣可以避免過早抽象化，導致介面很多但沒有一條完整流程真正可用。[cite:65][cite:72][cite:81][cite:96]

| 階段 | 目標 | 建議優先度 |
|---|---|---|
| Phase 1 | Claude Code baseline 可用 | P0 [cite:65][cite:72] |
| Phase 2 | 新增 API key backend | P1 [cite:81] |
| Phase 3 | `.env` 切換 provider / model | P1 [cite:90][cite:95] |
| 延伸項目 | 觀測性、fallback、路由、成本治理 | P2 [cite:95][cite:98] |

## Done 定義

每個 backlog item 建議至少符合以下 done criteria，才能算完成並進入下一階段。[cite:109][cite:115]

- 有明確程式碼落地，不只是文件描述。[cite:109]
- 有最小可驗證流程，例如可手動測試或有簡單自動測試。[cite:102]
- 錯誤處理已涵蓋常見失敗情境。[cite:96]
- 介面定義清楚，沒有把 provider-specific 細節洩漏到不相關模組。[cite:81][cite:96]
- 若涉及設定，已同步更新 `.env.example` 與啟動檢查。[cite:94][cite:100]
