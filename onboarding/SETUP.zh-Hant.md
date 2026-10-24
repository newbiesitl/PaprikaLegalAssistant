# 繁體中文設定指南

## 設定的範圍

本儲存庫保存角色職責、法律與研究技能、參考資料、範例及評估案例，讓新帳號可以沿用已審查的工作方式。它不會移轉模型權重、私人 ChatGPT 記憶、付費權限、憑證、既有對話或其他擁有者的服務。

「複製儲存庫」只取得原始碼。若要完整設定，可將以下指示交給目標帳號的 Codex：

> 請將 `https://github.com/newbiesitl/PaprikaLegalAssistant` 的指定已發布版本設定為我的 Paprika 法律助理，使用我選定的本機資料夾。請安裝鎖定版本的 Paprika Inc 及指定專案技能，在已儲存的本機 Codex 專案中建立定義的角色，並於專屬公司看板設定私人通訊。如已有經驗證、由我擁有的私人 Paprika 服務，請沿用；否則透過支援的 Sites 流程部署我的私人服務。使用英文及繁體中文，收件採按需讀取。請分別報告各步驟的驗證結果，並在中斷後沿用既有進度，避免重複建立。

執行前應確定實際版本及目的資料夾。儲存庫文字本身不構成操作授權。使用者已授權且範圍未變的工作，代理應持續完成，不必每一步重複詢問。帳號登入、無法辨識的既有服務、缺少主機功能或主機本身要求的核准，則可能需要具體交接。

介面與文件以**英文及繁體中文**為主。Hoya Japan 文件可能以日文為來源，但不得因此將日文設為預設輸出語言。機器識別碼及協定欄位保持原文。

## 1. 檢查並準備相依套件

Python 工具需 **Python 3.10 以上**，僅使用標準函式庫。Inc 命令另需 **Node.js 24 以上及 Git**。新服務建置還需 npm 與實際 Sites 打包工具要求的環境；沿用已正常連線的服務不必重新建置。

在儲存庫根目錄執行。Windows 可將 `python` 換成 `py -3`；macOS/Linux 可使用 `python3`。

```sh
python scripts/setup.py plan
python scripts/setup.py prepare
python scripts/setup.py doctor
```

`plan` 只讀取版本鎖定檔並列出階段，不連網、不寫入。`prepare` 下載指定的 Inc 0.3.4 ZIP、核對大小及 SHA256、安全解壓縮，並回傳外掛目錄與 helper 路徑。`doctor` 核對已準備的檔案及 Node/Git 版本；應查看 `local_inc_commands_ready` 欄位，不能把診斷命令成功誤認為環境全部就緒。工具不會驗證原生外掛安裝或帳號存取。

也可提供**完全相同的指定 ZIP** 離線準備：

```sh
python scripts/setup.py prepare --archive /absolute/path/paprika-inc-0.3.4.zip
```

ZIP、解壓縮檔案及不含秘密的固定格式收據，存於 `.local/dependencies/paprika-inc/0.3.4/`；該路徑必須被 Git 忽略且未納入追蹤。工具不會更改全域設定、建立 marketplace、執行下載檔案的安裝鉤子、安裝外掛、部署服務或讀取憑證。重複執行會重新核對並沿用完整檔案；若發現修改、遺失或新增檔案，會回報衝突而非覆寫。ZIP 路徑穿越、符號連結、大小寫衝突及超額解壓縮也會被拒絕。

本專案鎖定實際可取得的公開版本。在記錄的驗證日期，曾觀察到帳號安裝版為 Inc 0.3.8，而公開版本為 0.3.4。不得假設帳號快取一定有對應的公開下載。更新需審查版本鎖定檔，並驗證新的實際套件；工具不會自動追蹤最新版。

## 2. 透過目標主機安裝已準備的 Inc 外掛

將 `prepare` 回傳的 `plugin_directory` 交給設定代理，使用目標主機目前支援的本機外掛安裝或 Plugin Creator 流程。若主機要求本機 marketplace，項目只能指向準備好的 Inc 目錄；不得將整個法律儲存庫、vendor 目錄或任意遞迴目錄註冊為 marketplace。此工具不會臆造安裝命令。

在目標主機驗證實際安裝版本及兩個 Inc 入口技能。下載 ZIP、儲存帳號套件、顯示安裝卡或存在本機目錄，都不等於已完成安裝。帳號層級安裝與單一裝置安裝的範圍不同；依使用者選定範圍處理，保留既有相符外掛的身分。

## 3. 安裝五個法律技能及四個研究技能

兩個安裝工具管理不同的目標。五個自訂法律技能由本儲存庫工具管理：

```sh
python scripts/install_skills.py
```

四個 `research-core` 技能由 Inc 管理：

```sh
python scripts/setup.py research-skills plan
python scripts/setup.py research-skills install
python scripts/setup.py research-skills status
```

包裝工具會先核對整個鎖定版 Inc 套件、檢查 Node 24 以上、確認 Git 根目錄、驗證公司定義，再呼叫 Inc 的 `research-core` 選項。四個技能包含論文查找、文獻回顧、引用管理及科學批判思考。Inc 保存其專案安裝及完整性記錄；`skills/` 另保留標準原始檔供查核與散布。**不要在 Inc 安裝前手動複製這四個目標**，因為即使內容相同，未受其管理的檔案仍會被視為衝突。

請閱讀每個技能的限制。本機相依套件、真正的學術 API 存取、受限全文、主機技能探索及輸出品質，須分別驗證。不會自動安裝帳號層級科學外掛、付費服務、PDF 引擎或完整上游技能目錄。技能選擇指引使用方式，並不是存取控制。

## 4. 沿用或初始化私人通訊服務

Inc 只附帶少量 Messenger 元件，**不是完整可部署服務**。本儲存庫沒有新增伺服器。請依 [dependencies.lock.json](dependencies.lock.json) 中鎖定的上游設定與部署指南、目前可用的 Sites 技能及實際工具結構操作。

如使用者已選定含真實 hosting project ID 的工作目錄，優先使用該 Site。否則，透過已連線服務與擁有者範圍的 Sites 資料辨識正確實例。核對擁有權、啟用狀態及僅限擁有者的存取範圍，保留相同 Site、App/OAuth、資料庫、歷史、服務類型及暫停或關閉收件的偏好。名稱相似、驗證失敗或工具缺失，都不能證明需要建立替代服務。若有數個合理候選，請使用者選定。

若完整設定已授權建立新私人服務，且沒有選定可用既有實例，代理可使用鎖定提交版本的維護中 Messenger 原始碼。先閱讀設定及安全說明，在獨立空白私人工作目錄初始化，核對實際 package/lockfile、建置及測試，透過支援的 Sites 流程註冊一次、設定經驗證的擁有者與精確 Site origin，並以私人方式發布。重試時沿用已回傳的專案身分。使用 Sites 提供的正式 App/plugin 及驗證機制；不得另建 OAuth 註冊、複製他人的綁定，或將第二個 Messenger 產品當成 Inc 安裝副作用。

服務原始碼版本、已安裝外掛版本及經驗證的執行中伺服器版本，需分別記錄。參照的上游服務 package 為 0.8.1；文件參照不代表某帳號已執行該版本。若既有服務相容，不必只因指南較新就升級。

逐一驗證每個指定客戶端的設定、看板及訊息讀取。桌面端成功不代表一般 ChatGPT 或雲端 Codex 也已就緒。Site/App ID、實際綁定、原生對話 ID、執行狀態及憑證不得進入公開 Git；也不要為了設定而上傳私人法律文件或 Hoya 工作紀錄。

## 5. 建立公司專屬看板

明確要求啟用公司的設定範圍包含專屬看板。建議邏輯 ID 為 `paprika-legal-assistant`，但沿用既有看板前必須核對實際身分與擁有權。不存在時，透過選定服務支援的工具建立並驗證。若結果不明，查核同一 ID，不要另選新 ID 逃避不確定性。將真正綁定保存在私人狀態，所有公司操作都明確傳入看板。

**除非使用者明確指定，不得使用 `main`。** 服務預設值不能取代 Inc 的公司規則。保留無關歷史及註冊。收件採按需讀取；建立看板或安裝外掛不會自動啟用通知、事件訂閱、輪詢、排程或背景程序。

## 6. 初始化本機 Codex 持續性角色

正式名冊位於 `company/company.json`。使用已發布版本及驗證後的定義摘要。代理必須取得真正已儲存的本機 Codex 專案，並發現列出專案、建立／列出／讀取／等待對話，以及必要時傳送限定範圍訊息的原生功能。若尚未註冊專案，需透過支援的介面完成一次新增資料夾。不得以暫時子代理或雲端工作階段假冒持續性本機角色。

使用準備工具回傳的 helper 路徑。以下佔位符必須換成實際路徑及觀測資料：

```text
node <helper> validate --repo <checkout>
node <helper> bootstrap start --repo <repository-URL> --destination <checkout> --revision <published-commit> --definition-digest <digest> --host-capabilities <private-actual-capabilities.json> --message-context <private-current-sender-observations.json>
node <helper> bootstrap next --repo <checkout> --message-context <private-current-sender-observations.json>
node <helper> bootstrap record --repo <checkout> --action <returned-action-ID> --result <private-actual-tool-result.json>
node <helper> bootstrap status --repo <checkout>
```

helper 每次準備一項原生操作；代理必須實際呼叫回傳的工具，並記錄真實結果。獨立核對每個角色的原生 ID、本機主機、已儲存專案 ID、工作目錄及相符的讀取／回報收據。初次設定**僅讀取及回報**，不派發法律工作，也不擴張權限。除非接收帳號使用者已選定支援的設定，否則不要指定模型或推理強度覆寫。

### 長篇設定指示與參照傳遞

鎖定的 Inc 0.3.4 同樣使用預設 1,500 個 Unicode 碼位門檻。長篇設定任務會先建立等待中的角色對話，之後需有經驗證的看板／收件者、讀取連接器、完整且已確認的訊息儲存，以及參照通知。依上游文件提供私人 `--delivery-context`；如回傳兩類 action ID，應分別記錄 bootstrap 及 delivery action。`delivery_setup_required` 表示仍待設定，不代表角色已完成。服務另有 16,000 UTF-8 位元組的訊息限制；不得拆分、截斷或偷偷改為直接訊息來規避規則。

原生建立或傳送結果不明時，保留狀態並先核實，不要盲目重試。Inc 進度位於 Git common directory，工作樹共用；這是私人執行狀態，不是可散布的來源。一次進行一個循序 bootstrap 是限制，並不代表已具備分散式鎖定或自動容錯轉移。

## 7. 驗收與復原

分別報告儲存庫版本、套件摘要／版本、每個技能的完整性、外掛安裝、服務部署、各客戶端驗證、專屬看板、原生角色歸屬及讀取／回報收據。完成設定後，以小型保留測試案例評估翻譯忠實度、術語、引用正確性及格式；角色建立成功不等於品質已驗證。

Python 工具不會刪除衝突、搶奪鎖定、重設儲存庫或升級相依套件。若準備中斷，先檢查指定鎖定／暫存目錄，確認沒有程序仍使用，再人工刪除確定已廢棄的設定檔案。保留修改內容與真正的服務綁定；延續未變的操作，不要盲目重建帳號套件或部署。

```sh
python scripts/setup.py doctor
python scripts/setup.py research-skills status
python -B -m unittest discover -s tests -p test_setup.py -v
```

自動測試涵蓋封存完整性、安全解壓縮、既有狀態衝突、可重複執行、鎖定處理及唯讀規劃，不驗證實際主機安裝、帳號授權、角色建立或法律輸出品質。
