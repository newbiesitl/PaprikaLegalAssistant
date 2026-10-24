# Setup / 設定

Paprika Legal Assistant is a portable repository for legal study, research and translation workflows. Its interface and documentation use **English and Traditional Chinese**. Japanese can be a source language for Hoya Japan materials; it is not the default output language.

Paprika 法律助理提供可移轉的法律學習、研究及翻譯工作流程。介面與文件以**英文及繁體中文**為主。Hoya Japan 文件可能以日文撰寫，但不因此將日文設為預設輸出語言。

- [English setup guide](SETUP.en.md)
- [繁體中文設定指南](SETUP.zh-Hant.md)
- [Instructions for the onboarding agent / 設定代理操作指引](AGENT-SETUP.md)
- [Verified dependency versions / 已驗證相依版本](dependencies.lock.json)

## Start / 開始

From the repository root, use Python 3.10 or later. On Windows, `py -3` can replace `python`; on macOS/Linux, use `python3` when appropriate.

在儲存庫根目錄執行，需 Python 3.10 以上。Windows 可使用 `py -3`；macOS/Linux 可使用 `python3`。

```sh
python scripts/setup.py plan
python scripts/setup.py prepare
python scripts/setup.py doctor
```

`prepare` downloads the exact reviewed Inc ZIP, verifies its size and SHA256, and extracts it into ignored `.local/dependencies/`. It **prepares files only**. The plugin still needs the target host's supported installation flow; private service connection and persistent role chats need the agent-assisted steps in the guide.

`prepare` 會下載指定且已審查的 Inc ZIP、核對大小及 SHA256，並解壓縮至 Git 忽略的 `.local/dependencies/`。它**只準備檔案**。外掛安裝仍須使用目標主機支援的流程；私人服務連線及持續性角色對話則依指南由代理逐步完成。

The helper reports preparation, installation handoffs, service access and native-role setup as distinct states. A successful command does not certify translation quality or a connected account.

工具會分別報告檔案準備、安裝交接、服務存取及角色設定狀態。命令成功不代表翻譯品質已通過驗收，也不代表帳號已連線。

## Suggested status labels / 建議狀態標籤

| Code | English | 繁體中文 |
|---|---|---|
| `prepared` | Files prepared | 檔案已備妥 |
| `pending` | Pending | 待處理 |
| `blocked` | Blocked | 受阻 |
| `verified` | Verified | 已驗證 |
| `unverified` | Unverified | 尚未驗證 |
| `on_demand` | On demand | 按需讀取 |

These are this project's authored labels. They do not rename upstream UI controls or translate protocol keys.

這些標籤用於本專案文件與介面，不會更改上游介面名稱或協定欄位。
