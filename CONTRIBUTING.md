# Contributing / 貢獻指南

Use focused changes with a clear task, source, and review scope. Original
contributions are offered under the root MIT license. Preserve the notices and
applicable licenses of reused material.

## Workflows and examples

- Describe the user goal, inputs, output, and observable checks.
- Keep each skill self-contained and its metadata specific to real trigger
  conditions. Put supporting resources inside the skill directory.
- Keep English and Traditional Chinese authored interface content aligned.
- Use synthetic examples or material explicitly approved for public reuse.
  Never submit workplace documents, personal information, service bindings,
  tokens, or private conversation transcripts.
- Label corrections by scope and provenance. Keep development examples and
  evaluation cases separate.

## Research vendor updates

The four `research-core` skills are a selected upstream subset. Update their
source pin, complete file hashes, notices, and portability notes together.
Keep the canonical source consistent with the pinned Inc research installation.
Do not edit a single vendor instruction silently or enable optional external
integrations without updating the capability documentation.

## Validation

Run `python3 scripts/check_repo.py` and `python3 -m unittest discover -s tests -v`.
After preparing the pinned Inc dependency, validate the company through its
`inc.mjs validate --repo .` command. For workflow changes, use relevant fresh
cases; installing files or passing mechanical checks does not establish legal
or translation quality. Record the exact version assessed and remaining limits.

Ask for independent review of substantive changes. Respect existing branch
protections; review is separate from authority to merge or publish.

請提交範圍明確的變更，說明目的、來源、驗證方式與限制。原創貢獻採 MIT 授權，
第三方資料保留原授權。雙語內容應保持一致；僅使用合成資料或獲准公開的範例。
真實工作文件、私人對話、憑證及帳號綁定不得提交至公開儲存庫。
