# Paprika Legal Assistant / Paprika 法律助理

Read [README.md](README.md), the [company manifest](company/company.json), and
the relevant role contract. This repository defines an independent assistant
company for LL.M. (Master of Laws) study, legal research, legal translation, and
configurable Hoya Japan office support. It contains no Hoya policies or real
workplace documents and makes no claim of Hoya affiliation.

## Start a task / 開始任務

1. Select **Study / 學習** or **Legal Work / 法務工作** from the actual request.
   Keep their private documents and retrieval scope separate.
2. Keep interface language (`en`, `zh-Hant`), response language, source/target
   languages, jurisdiction, and material date independent. Japanese source
   documents are supported; office location does not establish governing law.
3. Read the relevant canonical workflow in `skills/` before doing substantive
   work. Use the task-specific source documents and profile supplied by this
   user. Example profiles and synthetic fixtures contain no approved facts.
4. Ask only for missing information that materially changes the result. Continue
   unaffected work with stated assumptions. Preserve source ambiguity.
5. Deliver a readable document in the requested format. Keep translation,
   explanation, and proposed substantive edits distinguishable. Keep detailed
   diagnostics in supporting records.

請依實際任務選擇學習或法務工作模式；介面以英文及繁體中文為主，文件語言與法域
另行指定。先閱讀適用技能，僅使用已提供的政策與案件資料。譯文、說明及實質修訂
建議應明確區分，交付成果須清晰易讀。

## Workflow routing / 工作流程

| Request | Read |
| --- | --- |
| Assigned readings, case brief, discussion preparation / 課程閱讀、判例摘要 | `skills/legal-study/SKILL.md` |
| Cases, legislation, legal propositions / 判例、法規、法律主張 | `skills/legal-research/SKILL.md` |
| Translation / 翻譯 | `skills/legal-translation/SKILL.md` |
| Bilingual fidelity review / 雙語忠實度覆核 | `skills/translation-review/SKILL.md` |
| Email, attachments, matter records / 郵件、附件、案件整理 | `skills/hoya-legal-work/SKILL.md` |
| Scholarly discovery / 論文搜尋 | `skills/paper-lookup/SKILL.md` and its `INC-PORTABILITY.md` |
| Literature synthesis / 文獻回顧 | `skills/literature-review/SKILL.md` and its `INC-PORTABILITY.md` |
| Bibliographic metadata / 文獻書目 | `skills/citation-management/SKILL.md` and its `INC-PORTABILITY.md` |
| Empirical evidence appraisal / 實證證據評估 | `skills/scientific-critical-thinking/SKILL.md` and its `INC-PORTABILITY.md` |

Doctrinal legal research needs primary authority and jurisdiction/date checks.
DOI existence, citation counts, a clinical evidence hierarchy, and model
agreement do not establish legal authority or support for a proposition.

## Setup / 安裝設定

For a request to **set up or initialize this company**, follow
[onboarding/README.md](onboarding/README.md). The setup request may cover the
documented stages; reuse that authorization without repeated confirmations.
Cloning or merely reading this file does not authorize account changes.

Run `python3 scripts/setup.py plan` to inspect prerequisites and
`python3 scripts/setup.py prepare` to prepare the verified Paprika Inc package.
Follow the exact supported host installation, private service, project, and
native role steps in the guide. Do not invent plugin commands, App IDs, host
tools, or completion receipts. Preserve an existing compatible owner-private
Paprika service; reconnect the recipient's own account when needed.

Use a dedicated company board. Initial role bootstrap is read/report onboarding.
Actual later task dispatch and outbound messages require the user's applicable
scope. Never substitute temporary collaboration agents for persistent native
Codex project chats. Report installed files, authenticated services, native
onboarding, and output quality separately.

## Data and changes / 資料與變更

- Keep real documents, account profiles, credentials, Site/App/native chat IDs,
  service bindings, and installation journals in ignored private locations.
- Commit only reusable procedures, permitted references, and clearly marked
  synthetic or approved de-identified examples.
- Follow `company/ownership.json`; it assigns review responsibility, not access.
- Preserve upstream research skill files and license notices. Record changes
  and provenance instead of silently editing the vendor subset.
- Review `evaluation/README.md` when testing behavior. Do not use its cases as
  demonstrations and then claim independent held-out performance.
- Preserve explicit model choices and record what the host actually applied.
  This repository does not force a model or grant legal credentials.
