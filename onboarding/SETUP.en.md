# English setup guide

## What setup does

The repository carries role contracts, reusable legal/research workflows, references, examples and evaluation cases. A new account can reuse that reviewed material. Model weights, private ChatGPT memory, paid access, credentials, live chats and another owner's service are not transferred.

A clone-only request obtains source. The following full request gives an onboarding agent a concrete scope to finish:

> Set up Paprika Legal Assistant from `https://github.com/newbiesitl/PaprikaLegalAssistant` at the selected published revision in my chosen local folder. Install its pinned Paprika Inc dependency and the selected project skills, create the roles in the saved local Codex project, and set up private communication on a dedicated company board. Reuse my verified owner-private Paprika service when available; otherwise deploy my own private service through the supported Sites workflow. Use English and Traditional Chinese. Keep receiving on demand. Report each verified stage separately and resume partial progress without creating duplicates.

Select the actual revision and destination before executing the request. The repository's instructions do not supply authority independently of the user. The agent should continue unchanged authorized work without repeatedly asking for the same approval. Account sign-in, an ambiguous service choice, unavailable host capabilities or a native approval may require a specific handoff.

## 1. Inspect and prepare the dependency

Requirements for the Python helper: **Python 3.10+**, standard library only. For Inc commands: **Node.js 24+ and Git**. New service builds also require npm and the selected Sites packager's actual prerequisites. Existing working service reuse does not require a service build.

```sh
python scripts/setup.py plan
python scripts/setup.py prepare
python scripts/setup.py doctor
```

`plan` reads the lock and prints stages without network or writes. `prepare` downloads and verifies the exact Inc 0.3.4 release, safely extracts it, and reports the plugin directory and helper path. `doctor` verifies prepared bytes and checks local Node/Git versions; its `local_inc_commands_ready` field is separate from its successful diagnostic execution. Native plugin installation and account access remain unverified by this script.

An offline copy of the **same exact ZIP** is supported:

```sh
python scripts/setup.py prepare --archive /absolute/path/paprika-inc-0.3.4.zip
```

The helper stores the ZIP, extracted package and a non-secret deterministic receipt under `.local/dependencies/paprika-inc/0.3.4/`. That path must be ignored and untracked. It does not change global configuration, create a marketplace, run downloaded hooks, install the plugin, deploy a service or read credentials. Repeating preparation revalidates and reuses intact bytes. Modified, missing or extra files cause a visible conflict instead of replacement. Unsafe ZIP paths, symlinks, case collisions and oversized extraction are rejected.

The lock pins the publicly available release rather than assuming that an account-installed package has a public equivalent. At the recorded verification date, an inspected account had Inc 0.3.8 while the public release was 0.3.4. Updates require a reviewed lock change and checks against the new actual artifact; there is no automatic latest-version upgrade.

## 2. Install the prepared Inc plugin through the target host

Give the onboarding agent the `plugin_directory` returned by `prepare`. Use the target host's currently supported local plugin installation or Plugin Creator workflow. If a local marketplace is necessary, its explicit entry must select that prepared Inc directory. Do not register this whole repository, its vendor directories or an arbitrary recursive tree as a marketplace. The helper does not invent a CLI installation command.

Verify the installed plugin version and the two Inc entry skills in the target host. A downloaded ZIP, account save, displayed card or local directory is not proof that the host installed the plugin. Account installation and a device-local installation have different scopes; follow the user's selected scope and preserve any existing matching plugin identity.

## 3. Install the five legal skills and the four research skills

The two installers own different targets. Use the repository's legal-skill installer for the five custom legal skills:

```sh
python scripts/install_skills.py
```

Then use Inc for its four `research-core` skills:

```sh
python scripts/setup.py research-skills plan
python scripts/setup.py research-skills install
python scripts/setup.py research-skills status
```

This wrapper revalidates the entire pinned Inc package, checks Node 24+, confirms the selected Git root, validates the company definition and invokes only Inc's `research-core` selection. The four skills are paper lookup, literature review, citation management and scientific critical thinking. Inc manages their project installation and integrity journal. Their canonical source is also retained in `skills/` for audit and distribution; do not copy those four targets manually before Inc installation, because unmanaged files conflict even when identical.

Read each skill's limitations. Local dependency availability, actual scholarly API access, restricted full text, native skill discovery and quality are separate checks. No account-wide scientific plugin, paid service, PDF engine or full upstream catalog is installed. Skill selection guides use; it is not an access-control boundary.

## 4. Reuse or initialize the private communication service

Inc itself contains a small pinned Messenger component, **not the complete deployable service**. No new server is included in this repository. Follow the exact upstream setup/deployment references in [dependencies.lock.json](dependencies.lock.json), the currently available Sites skill and actual native tool schemas.

For an existing service, first respect a user-selected workspace's real hosting project ID. Otherwise inspect connected service metadata and owner-scoped Sites metadata to identify the intended instance. Verify ownership, active state and owner-only audience. Reuse the same Site, App/OAuth identity, database/history, service type and paused/off receiving preferences. A title match, failed authentication or missing tool is insufficient reason to create a replacement. Resolve genuinely ambiguous instances with the user.

If the full request authorizes a new private service and no existing instance was selected, the agent can use the maintained Messenger service source at the pinned upstream commit. Read that source's setup/security guidance, initialize an empty private workspace, verify its actual package/lockfile, build/test, register one private Site, configure the verified owner and exact Site origin through supported runtime settings, and publish with the supported Sites source/version workflow. Preserve that returned project identity through retries. Use Sites' canonical App/plugin and authentication boundary. Do not construct a new OAuth registration, copy another owner's binding, or install a second Messenger product as an Inc side effect.

Keep the service package version, installed plugin version and running authenticated server version separate. The referenced upstream service package is 0.8.1; the source reference is guidance, not evidence that a particular account runs that version. A compatible existing service need not be upgraded solely because the guide is newer.

Verify authenticated configuration and board/message reads in every requested client. Desktop success does not establish ordinary ChatGPT or cloud Codex readiness. Keep owner-specific Site/App IDs, bindings, native chat IDs, runtime state and credentials outside public Git. Do not store legal source documents or Hoya work records in a public repository merely to finish setup.

## 5. Establish the dedicated company board

An explicit live company setup request includes a dedicated board. The proposed logical ID is `paprika-legal-assistant`; confirm its actual identity and ownership before reusing an existing board. If absent, create it through the selected service's supported tool and verify the result. On uncertain outcomes, reconcile that same ID instead of choosing another one. Keep the actual binding private and pass the board explicitly to every company operation.

**Do not use `main` unless the user explicitly chooses it.** Service defaults do not override this Inc company rule. Preserve unrelated histories and registrations. Use on-demand receiving; board creation or plugin installation does not enable notifications, event subscriptions, polling, schedules or background processes.

## 6. Bootstrap the persistent local Codex roles

The canonical roster is in `company/company.json`. Use its published revision and the validated definition digest. The agent must discover the real saved local Codex project and these native capabilities: project listing, thread creation/listing/reading/waiting, and scoped thread messaging when needed. Missing saved-project registration requires the supported one-time add-folder app action. This workflow cannot be emulated by ephemeral subagents or cloud sessions.

Use the helper path returned by preparation. The following placeholders must be replaced with actual paths and observations:

```text
node <helper> validate --repo <checkout>
node <helper> bootstrap start --repo <repository-URL> --destination <checkout> --revision <published-commit> --definition-digest <digest> --host-capabilities <private-actual-capabilities.json> --message-context <private-current-sender-observations.json>
node <helper> bootstrap next --repo <checkout> --message-context <private-current-sender-observations.json>
node <helper> bootstrap record --repo <checkout> --action <returned-action-ID> --result <private-actual-tool-result.json>
node <helper> bootstrap status --repo <checkout>
```

The helper prepares one native action at a time. The agent invokes exactly that supported tool and records its actual result. Independently verify each role's native ID, local host, saved project ID, cwd and completed matching read/report receipt. The initial onboarding is **read/report only**; it does not dispatch legal work or grant new powers. Do not set model/effort overrides unless the recipient chooses supported settings.

### Long onboarding and reference delivery

The pinned 0.3.4 source also applies the 1,500-Unicode-code-point default delivery policy. A long onboarding task creates a waiting role chat first, then requires a verified board/recipient, retrieval connector, complete confirmed message storage and reference notification. Supply the documented private `--delivery-context` and record both bootstrap and delivery action IDs when returned. `delivery_setup_required` means setup is pending; it is not successful onboarding. The service's 16,000-UTF-8-byte body limit also applies. Do not split, truncate or silently inline a long task to evade the policy.

Preserve uncertain native create/send results and reconcile them before retrying. Inc's progress lives in the Git common directory, shared by worktrees. It is private runtime state, not a reusable source file. One sequential bootstrap at a time is a limitation, not a guaranteed distributed lock or automatic failover system.

## 7. Acceptance and recovery

Report the repository revision, package hash/version, per-skill integrity, plugin installation, service deployment, per-client authentication, dedicated board, native role membership and read/report receipts separately. Run small held-out translation/research tasks to assess fidelity, terminology, citation correctness and formatting after setup; role creation does not establish quality.

The Python helper deliberately does not erase conflicts, steal locks, reset repositories or upgrade dependencies. If preparation was interrupted, inspect the named lock/staging directory and confirm that no process still uses it before manually removing only abandoned setup artifacts. Preserve modified files and actual live bindings. Resume the unchanged operation instead of rerunning account creation or deployment blindly.

Useful checks:

```sh
python scripts/setup.py doctor
python scripts/setup.py research-skills status
python -B -m unittest discover -s tests -p test_setup.py -v
```

The automated tests cover archive integrity, unsafe extraction, ownership conflicts, idempotence, lock handling and read-only planning. They do not certify live host installation, account authentication, role creation or legal output quality.
