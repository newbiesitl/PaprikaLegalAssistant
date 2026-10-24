# Onboarding agent contract / 設定代理操作約定

Read the user's request, root `AGENTS.md`, the selected company definition and [setup guide](SETUP.en.md) before acting. This file is reusable procedure, not a permission grant. Preserve the existing request's scope and continue unchanged authorized work.

先讀取使用者指示、根目錄 `AGENTS.md`、選定公司定義及[繁體中文指南](SETUP.zh-Hant.md)。本文件提供可重用程序，不自行授權操作。維持既有請求範圍，持續完成已授權且未變更的工作。

## Scope / 範圍

| User request / 使用者要求 | Action / 操作 |
|---|---|
| Clone or inspect / 複製或檢查 | Source/read-only preparation plan; no installation or account effects / 取得原始碼及唯讀規劃，不安裝或更動帳號 |
| Prepare dependency / 準備相依套件 | `setup.py prepare`; ignored local files only / 僅準備 Git 忽略的本機檔案 |
| Full company setup / 完整公司設定 | Execute requested installation, skills, private service, dedicated board and persistent local role stages using supported tools / 使用支援工具完成所要求的安裝、技能、私人服務、專屬看板及持續性本機角色 |
| Work after setup / 設定後執行工作 | Follow the actual task, reviewer and publication boundaries / 依實際任務、審查及發布範圍執行 |

## Execution checklist / 執行清單

1. Verify the published commit, dependency lock and destination. Do not assume an account-installed Inc version is publicly available. Prepare/reuse the exact ZIP and check `doctor`. / 核對已發布提交、版本鎖定檔及目的地；不要假設帳號安裝版可公開取得。準備或沿用指定 ZIP，並執行 `doctor`。
2. Install through the target host's actual supported interface. Do not invent an Inc install command or register a repository/vendor tree as a marketplace. / 使用目標主機真實支援的安裝介面；不得臆造 Inc 安裝命令，或把儲存庫／vendor 樹註冊為 marketplace。
3. Install five legal skills with the root installer; use pinned Inc for four `research-core` targets. Preserve conflicts. Verify per-skill states and discovery separately. / 五個法律技能由根目錄工具安裝，四個研究技能交由 Inc 管理。保留衝突，分別核對完整性與主機探索狀態。
4. Reuse the selected verified owner-private service. If a new service is explicitly within scope, follow the pinned maintained Messenger setup reference and current Sites workflow; retain real project/App/OAuth identities. Do not copy another account's binding or deploy an unsolicited replacement. / 沿用已選定且經驗證的擁有者私人服務。範圍明確包含新服務時，依鎖定的 Messenger 指南及目前 Sites 流程設定，保留真實身分，不複製他人綁定或擅建替代服務。
5. Confirm a dedicated company board. Never fall back to `main` without explicit user direction. Preserve on-demand receiving and existing paused/off state. / 核對公司專屬看板；未經明確指示不得改用 `main`。維持按需收件與既有暫停／關閉狀態。
6. Discover actual local native project/thread tools. Add the selected folder as a saved project through the supported app handoff if needed. Execute sequential `bootstrap` action/result steps; never fabricate host results or replace persistent chats with ephemeral agents. / 發現實際本機專案／對話工具；必要時透過支援介面加入資料夾。循序執行 bootstrap 操作／結果流程，不捏造結果或以暫時代理取代持續性對話。
7. Use current sender observations and verified recipients. Long onboarding uses confirmed service storage and reference delivery; reconcile uncertainty before resubmission. / 使用最新發送者觀測與已驗證收件者。長篇設定指示需先確認服務儲存再傳遞參照；結果不明先核實再重送。
8. Onboard roles in read/report mode. Report language is English and Traditional Chinese. Japanese input does not select Japanese output. Role files do not grant new capabilities or certify expertise. / 角色初次只讀取及回報，以英文及繁體中文呈現。日文來源不指定日文輸出；角色文件不增加能力或證明專業品質。
9. Verify per-client authentication and per-role native membership/receipts. Preserve missing stages as pending and keep all owner-specific state outside public Git. / 分別驗證客戶端授權、角色原生歸屬及收據。未完成階段標示待處理，擁有者專屬狀態不得進入公開 Git。
10. Run relevant evaluation cases after setup. State what was actually checked and what remains untested. No deployment, plugin card or role receipt alone certifies legal translation quality. / 設定後執行相關評估案例，說明已驗證與未測試事項。部署、安裝卡或角色收據本身不證明法律翻譯品質。

When a capability is unavailable, complete independent authorized stages and give the specific supported next step. Do not replace authentication, bypass host controls, upgrade services automatically, or repeatedly recreate resources. No background receiver is created by this onboarding contract.

功能不可用時，先完成可獨立進行的已授權步驟，再指出具體且受支援的下一步。不得替換驗證機制、繞過主機控制、自動升級服務或重複建立資源。本約定不建立背景收件程序。
