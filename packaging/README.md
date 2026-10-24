# Distribution / 發布方式

## Repository setup

The Git repository is the complete company package: roles, ownership,
onboarding, reusable skills, templates, profiles, evaluation and setup helpers.
Follow the [onboarding guide](../onboarding/README.md) when creating the local
company and connecting the recipient's own private service.

Git 儲存庫包含完整團隊設定、角色、技能、範本、評估及設定工具。建立本機團隊與
連接接收者自己的私人服務時，請依[入門指南](../onboarding/README.md)執行。

## Optional skills-only plugin

Run from the checkout:

```sh
python3 scripts/check_repo.py
python3 scripts/build_plugin.py
```

The builder produces `.local/dist/paprika-legal-assistant-0.1.0.zip` and reports
its SHA-256. The archive contains one `paprika-legal-assistant/` directory with
`plugin.json`, the nine self-contained skill directories, provenance and license
notices. Entry order, timestamps and file modes are normalized so unchanged
sources produce the same ZIP bytes in the same packaging environment.

The company roster, onboarding scripts and account bindings are not part of
this skills-only archive. For the full team, use the repository route above.
When a host loads both project skills and plugin skills, verify which copy it
selects and avoid unintended duplicate installations.

封裝工具會產生僅含九個技能及相關資源、來源與授權聲明的 ZIP，並輸出 SHA-256。
公司角色與設定腳本仍由 Git 儲存庫提供。若同時使用專案技能及插件技能，請核對
實際載入版本，避免不必要的重複安裝。

Use the receiving host's supported plugin installation flow. Building an archive
does not register a plugin, authenticate a service, create an MCP endpoint, or
deploy a private site. The Paprika Inc and Messenger setup uses recipient-specific
connections described in the onboarding guide.

## Updating a release

Review changes to the legal workflows and run the affected evaluation cases.
Keep research payload bytes and their [provenance](../provenance/research-core.json)
in agreement; update their public pins and notices together when adopting a new
upstream release. Bump `plugin.json` and the relevant company definition/role
versions deliberately, and record the scope in [CHANGELOG.md](../CHANGELOG.md).
Existing local installer conflicts require inspection and an explicit migration;
the installer does not silently replace recipient edits.
