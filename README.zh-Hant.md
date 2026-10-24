# Paprika 法律助理 · Paprika Legal Assistant

[English](README.md) · [安裝指南](onboarding/SETUP.zh-Hant.md) ·
[角色定義](company/company.json) · [評估方法](evaluation/README.md) · [MIT 授權](LICENSE)

這是一個以 Git 儲存庫定義的開源助理團隊，支援**法學碩士（LL.M.）學習、法律研究、
法律翻譯及辦公室法務工作**。本專案撰寫的介面內容、角色介紹及入門說明以**英文與
繁體中文**為主，亦支援日文來源文件。

首個工作設定為可自行調整的 **Hoya 日本法務支援範例**。本專案獨立開發，並非 Hoya
官方產品；儲存庫不包含 Hoya 內部政策、實際契約、個人資料或帳號憑證。

## 兩種使用模式

| 模式 | 常見工作 |
| --- | --- |
| **法學學習 / Study** | 指定閱讀、判例摘要、法律概念、課堂討論準備、研究備忘錄、文獻回顧及雙語筆記。 |
| **法務工作 / Legal Work** | 翻譯、郵件與附件分析、案件摘要、時序整理、文件版本比較及具來源依據的研究。 |

介面語言、回覆語言、文件來源及目標語言、適用法域與日期應分別設定。學習資料與
工作文件應維持各自的任務及檢索範圍。

## 在 Codex 開始使用

請在能存取目標資料夾的本機 Codex 對話中貼上：

> 請將 https://github.com/newbiesitl/PaprikaLegalAssistant 複製至新的本機專案資料夾，
> 並為我的帳號設定 Paprika 法律助理。先閱讀 AGENTS.md 及 onboarding/SETUP.zh-Hant.md。
> 請準備並安裝已鎖定版本的 Paprika Inc、安裝五個法律工作流程及四個研究技能，
> 初始化專屬公司看板與五個本機 Codex 持續性角色對話。若已有經驗證且由我擁有的
> 私人 Paprika 服務，請沿用；否則依文件中的 Paprika Messenger／Sites 流程建立
> 我自己的私人服務。使用英文及繁體中文，採按需收件，保留無關設定，逐項核實
> 安裝結果。請完成所有支援的步驟，並明確指出需要我登入或加入已儲存專案的操作。
> 未取得實際驗證資料前，請勿宣稱相關階段已完成。

此流程由 **Codex 協助執行**：本機依賴準備及技能安裝已有可執行工具；插件安裝、
私人服務部署、身分驗證與持續性角色對話建立，使用目標環境實際支援的工具。
單純執行 Git clone 不會自動進行帳號操作。詳見[完整安裝指南](onboarding/SETUP.zh-Hant.md)。

終端機本機準備指令：

```sh
git clone https://github.com/newbiesitl/PaprikaLegalAssistant.git
cd PaprikaLegalAssistant
python3 scripts/setup.py plan
python3 scripts/setup.py prepare
python3 scripts/install_skills.py
python3 scripts/setup.py research-skills install
python3 scripts/setup.py doctor
```

Windows 可將 `python3` 改為 `py -3` 或環境支援的 `python`。本專案以 Python 3.11+
為基準；Paprika Inc 的本機初始化需要 Node.js 24+ 與 Git。外部研究服務權限另行驗證。

## 五個角色

| 角色 | 主要職責 |
| --- | --- |
| [協調與知識管理](company/roles/coordinator/agent.md) | 釐清需求、安排流程、維護已認可的用語、範例與修正。 |
| [法學碩士學習與法律研究](company/roles/academic-legal-researcher/agent.md) | 課程準備、判例摘要、法律研究及文獻回顧。 |
| [Hoya 法務工作支援](company/roles/hoya-legal-support/agent.md) | 郵件、附件、委託事項、案件資料及時序整理。 |
| [法律翻譯](company/roles/legal-translator/agent.md) | 忠實翻譯、術語一致性、對照排版與獨立譯註。 |
| [品質與證據覆核](company/roles/quality-reviewer/agent.md) | 語意、完整性、來源支持、術語與呈現方式的覆核。 |

簡短任務可在同一對話中依流程完成；重大成果可另行覆核。角色名稱不代表已取得
任何專業資格。

## 套件內容

- 五個法律技能：學習、法律研究、翻譯、翻譯覆核及辦公室資料受理。
- 四個研究技能：論文搜尋、文獻回顧、引註管理與科學批判思考，保留來源及授權聲明。
- 雙語角色定義、空白設定範本及可重用的成果格式。
- 鎖定版本與雜湊值的依賴準備工具、不覆寫修改的技能安裝程序及恢復指南。
- 明確標示為合成資料的評估案例；不宣稱已證明實際法律品質或跨帳號表現等同。
- 僅含技能的插件設定與可重現封裝工具。私人服務由各使用者在設定時自行連接。

## 使用範例

- 「依這些指定讀物製作判例摘要，以英文及繁體中文解釋，並附精確來源位置。」
- 「將這份日文契約譯成英文，保留條款編號，譯註另列。」
- 「核對原文與譯文的義務、例外、當事人及金額是否改變，格式另行評估。」
- 「從郵件串整理委託人、相對方、附件語言及委辦事項，列出依據並標記未知欄位。」
- 「針對這個實證法律問題回顧文獻，說明搜尋範圍、篩選準則、發現與限制。」

## 私人資料及知識移轉

將設定範本複製至 `.local/profiles/` 後再填入個人或工作資料。實際課程檔案、公司
文件、服務綁定及個人識別資料應留在獲准的私人儲存位置。Hoya 設定檔僅為空白範例。

移轉的內容應是已覆核程序、允許使用的範例及具有適用範圍的修正。接收者應設定
自己的偏好及服務權限；模型、工具與對話脈絡仍會影響結果，須在接收帳號評估新任務。

## 開發及封裝

```sh
python3 scripts/check_repo.py
python3 -m unittest discover -s tests -v
python3 scripts/build_plugin.py
```

插件封裝檔位於不納入 Git 的 `.local/dist/`，內含技能及其所需資源，不含帳號連線
或私人資料。封裝完成不等於插件已安裝，仍須使用環境支援的安裝方式。

參閱[貢獻指南](CONTRIBUTING.md)、[第三方聲明](THIRD_PARTY_NOTICES.md)、
[知識管理指南](knowledge/README.md)及[版本紀錄](CHANGELOG.md)。

## 驗證範圍

首版提供原始碼、角色定義、本機設定工具及工作流程與評估材料。本機檢查結果列於
版本紀錄。接收帳號的身分驗證、原生持續性對話、私人服務部署及任務品質，必須在
實際目標環境分別驗證。本專案不提供新的法律資料庫或模型訓練服務。
