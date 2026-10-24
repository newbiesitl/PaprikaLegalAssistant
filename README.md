# Paprika Legal Assistant · Paprika 法律助理

[繁體中文](README.zh-Hant.md) · [Installation](onboarding/README.md) ·
[Roles](company/company.json) · [Evaluation](evaluation/README.md) · [MIT License](LICENSE)

An open-source, repository-defined assistant company for **Master of Laws
(LL.M.) study, legal research, translation, and legal office work**. Its authored
interface and onboarding use **English and Traditional Chinese**. Japanese
remains an available document source language.

The initial workplace profile is a configurable **Hoya Japan support example**.
This is an independent project, not an official Hoya product. It contains no
Hoya internal policies, contracts, personal records, or account credentials.

## Two profiles, shared methods

| Profile | Typical work |
| --- | --- |
| **Study / 法學學習** | Assigned readings, case briefs, legal concepts, discussion preparation, research memos, literature reviews, and bilingual notes. |
| **Legal Work / 法務工作** | Translation, correspondence and attachment analysis, matter summaries, chronology, document comparisons, and evidence-backed research. |

Interface language, response language, document source/target language,
jurisdiction, and applicable date are separate choices. Study and workplace
documents keep separate task and retrieval scope.

## Quick start in Codex

Paste this into a local Codex conversation with access to the desired folder:

> Clone https://github.com/newbiesitl/PaprikaLegalAssistant into a new local
> project folder and set up Paprika Legal Assistant for my account. Read
> AGENTS.md and onboarding/README.md first. Prepare and install the pinned
> Paprika Inc dependency, install the five legal workflows and four research
> skills, and initialize the dedicated company board and five persistent local
> Codex roles. Reuse my verified owner-private Paprika service if available;
> otherwise set up my own private service through the documented Paprika
> Messenger/Sites workflow. Use English and Traditional Chinese. Keep receiving
> on demand, preserve unrelated settings, and verify each setup stage. Continue
> all supported steps and identify any sign-in or saved-project action I must
> perform. Do not claim a stage is complete without its actual evidence.

The setup is **agent-assisted**: local preparation is executable; plugin
installation, private service provisioning, authentication, and persistent
role creation use the target host's supported tools. A plain Git clone does
not execute those account actions. See the [complete guide](onboarding/README.md).

For local preparation from a terminal:

```sh
git clone https://github.com/newbiesitl/PaprikaLegalAssistant.git
cd PaprikaLegalAssistant
python3 scripts/setup.py plan
python3 scripts/setup.py prepare
python3 scripts/install_skills.py
python3 scripts/setup.py research-skills install
python3 scripts/setup.py doctor
```

On Windows, use `py -3` or the supported `python` executable instead of `python3`.
Python 3.11+ is the project baseline; Paprika Inc's native checkout/bootstrap
needs Node.js 24+ and Git. External research access is checked separately.

## Five roles

| Role | 職責 | Contract |
| --- | --- | --- |
| Coordinator & Knowledge Steward | 協調、任務分派與知識管理 | [coordinator](company/roles/coordinator/agent.md) |
| LL.M. Study & Legal Research | 法學碩士學習與法律研究 | [academic-legal-researcher](company/roles/academic-legal-researcher/agent.md) |
| Hoya Legal Office Support | Hoya 法務工作支援 | [hoya-legal-support](company/roles/hoya-legal-support/agent.md) |
| Legal Translator | 法律翻譯 | [legal-translator](company/roles/legal-translator/agent.md) |
| Quality & Evidence Reviewer | 品質與證據覆核 | [quality-reviewer](company/roles/quality-reviewer/agent.md) |

Use only the roles a task needs. Small tasks can follow the same procedures in
one conversation. A role name does not establish professional credentials.

## What is included

- Five legal workflows: study, legal research, translation, translation review,
  and office intake.
- Four selected research skills: paper lookup, literature review, citation
  management, and scientific critical thinking, with retained provenance and
  license notices.
- Bilingual role definitions, example profiles, and reusable output templates.
- A pinned dependency preparer, non-overwriting project skill installation,
  onboarding and recovery instructions, and local checks.
- Synthetic evaluation cases with explicit limits; no claimed real-world
  legal acceptance or cross-account performance parity.
- A skills-only plugin manifest and reproducible package builder. The private
  Paprika service is connected per recipient during onboarding.

## Using the workflows

Examples after loading the repository or installed skills:

- “Prepare a case brief from these assigned readings. Explain it in English
  and Traditional Chinese, with pinpoint references.”
- “Translate this Japanese agreement into English. Preserve clause numbering
  and put translator notes in a separate section.”
- “Review this source and translation for changes in obligations, exceptions,
  parties, and amounts. Check layout separately.”
- “Extract the requester, counterparty, attachment language, and requested work
  from this email thread. Show the evidence and mark uncertain fields.”
- “Review the literature on this empirical legal question; document search
  scope, selection criteria, findings, and limitations.”

Keep translation, explanation, and proposed drafting changes distinct. For
legal research, verify the actual authority and applicable version; a valid
citation identifier alone does not verify the proposition.

## Privacy and knowledge transfer

Copy an example profile into `.local/profiles/` and populate it there. Keep
actual course files, workplace documents, account bindings, and user identities
in approved private storage. The repository's Hoya profile is a blank example.

Transfer reviewed procedures, permitted examples, and scoped corrections.
Each recipient supplies their own preferences and service access. Model
selection, tool access, and context still affect results; evaluate unseen tasks
on the actual receiving account.

## Development and packaging

```sh
python3 scripts/check_repo.py
python3 -m unittest discover -s tests -v
python3 scripts/build_plugin.py
```

The plugin archive is created under ignored `.local/dist/`. It includes the
skills and their supporting resources, not account connections or private data.
Use the host's supported plugin installation flow; archive generation itself
does not install a plugin.

See [CONTRIBUTING.md](CONTRIBUTING.md), [third-party notices](THIRD_PARTY_NOTICES.md),
the [knowledge guide](knowledge/README.md), and [release notes](CHANGELOG.md).

## Verification status

This initial release provides source, role definitions, local setup tooling,
and workflow/evaluation materials. Local validation is recorded in the release
notes. Recipient authentication, persistent native chats, private service
deployment, and task quality require verification on the actual destination.
The project does not provide a new legal database or a model-training service.
