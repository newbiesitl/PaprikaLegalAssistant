# Changelog / 版本紀錄

## 0.1.0 — 2026-10-24

Initial public source release of **Paprika Legal Assistant / Paprika 法律助理**.

### Included

- A Paprika Inc company definition with five roles for LL.M. study, legal
  research, Hoya office support, translation and quality review.
- English and Traditional Chinese interfaces, onboarding guides, role
  instructions and authored output templates. Document language and legal
  jurisdiction remain task-specific.
- Five original legal skills and four MIT-licensed research skills, with
  retained notices and per-file provenance.
- The verified public Paprika Inc 0.3.4 dependency, pinned by source revision,
  archive size and SHA-256. The preparer downloads it only when requested.
- Separate, conflict-preserving installation of five legal and four Inc-managed
  research skills into the selected local project.
- An optional reproducible skills-only plugin archive builder.
- Eight fictional evaluation fixtures, a blank comparison record, and a
  procedure for comparing outputs on the actual receiving account.

### Verification record

Checked on Linux with Python 3.12.14, Node.js 24.22.1 and Git 2.51.1:

- **24 automated tests passed**, covering archive verification/extraction,
  conflict preservation, install recovery, idempotence, locks and plugin staging.
- The real upstream ZIP was downloaded and its size and SHA-256 verified.
  Repeated preparation reused the verified dependency without replacing files.
- The pinned Inc helper accepted the five-role company definition. Definition
  input SHA-256:
  `36946a2743d2841cc9b2a4462dac8e709547e471d393c87ea3cd19372e2254e3`.
- All five legal skills were installed into a local test checkout; all four
  research skills were installed through Inc and reported intact. These are
  file-installation checks, not native host discovery receipts.
- The plugin builder produced a valid archive containing **97 files and nine
  skills**. Its regression test verified identical bytes on repeated builds.
- All 75 selected research payload files retain the pinned source hashes and
  license notices. Research APIs and optional Python dependencies were not
  provisioned as part of this local integration check.
- The repository checker passed: nine skill definitions, eight bundled legal
  assets, dependency/provenance agreement, role/ownership references and local
  links in the authored documentation. All five original skills also passed
  the skill-creator format validator.

The two initial model-assisted workflow smoke checks are described in
[evaluation/initial-smoke-check.md](evaluation/initial-smoke-check.md). They use
fictional closed inputs and are not a human legal review or a cross-account
comparison. The eight-case comparison template remains `not_run`.

### Recipient acceptance still required

The release does not assert that any recipient's plugin has been installed,
that a private site has been deployed or authenticated, or that five persistent
native role chats have been created. Those stages require the recipient's
supported host tools and their own service access. Native Windows/macOS setup
and actual legal-work quality have not been validated by this source release.

首版提供可移轉的角色、程序、範本及評估工具。各接收帳號的插件安裝、私人服務、
原生角色對話及實際法律工作品質，均須在目標環境分別驗證；本版本不宣稱已完成
跨帳號等效品質驗證。
