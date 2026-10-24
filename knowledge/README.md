# Reusable knowledge / 可重用知識

This directory contains the procedure for curating knowledge, not an approved
legal glossary or a corpus of client documents.

Store a proposed lesson with:

- A stable identifier and version.
- Its source or synthetic-example status.
- The original issue and accepted correction.
- A short explanation and the applicable language direction, document type,
  jurisdiction, and context.
- Review status and the kind of reviewer; identify a real reviewer only in an
  authorized private record.
- Tests affected and the date last checked.

Use `candidate`, `reviewed-for-stated-scope`, or `superseded` as explicit states.
An agent-generated example starts as `candidate`. Review a correction before
promoting it, and never generalize a matter-specific term to every contract.

Keep user profiles and real documents outside this public directory. A shared
workflow may retrieve only the material permitted for the current task/profile.
Do not mix workplace information into study examples automatically.

## Example record shape

```json
{
  "id": "synthetic-example-001",
  "version": "0.1.0",
  "status": "candidate",
  "source_kind": "synthetic",
  "issue": "Describe the observed problem.",
  "correction": "Record a proposed correction without asserting legal approval.",
  "reason": "Explain the observable difference.",
  "scope": {"source_language": null, "target_language": null, "jurisdiction": null},
  "reviewer_kind": "unreviewed",
  "last_checked": null
}
```

本目錄提供知識整理程序，不代表已核准的法律詞彙庫。修正紀錄須保留來源、問題、
修正理由、適用範圍與覆核狀態。AI 產生的範例先列為候選；私人工作資料與個人設定
應另行保存，亦不得自動混入學習資料。
