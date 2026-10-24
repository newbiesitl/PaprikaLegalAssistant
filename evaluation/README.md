# Evaluation / 評估

These are **synthetic review fixtures**, not real agreements, decisions, statutes,
office records, or legal ground truth. They test whether an assistant preserves
provided meaning, respects evidence limits, and follows a task's format. No model
evaluation result is implied by including these files.

這些資料全部為人工撰寫的虛構測試案例，不是真實合約、判決、法規或公司紀錄。預期檢查項目僅依據案例所提供的文字，不代表對任何法域的法律結論。

## Files

- [fixtures.json](fixtures.json): eight cases covering translation, legal source
  handling, study support, office extraction, and empirical review.
- [results-template.json](results-template.json): a blank record for an actual
  comparison. Its default status is `not_run`.

## Run a small transfer comparison

1. Record the repository commit, model/version if visible, relevant settings,
   enabled tools, account/project context, and date.
2. Run a fresh baseline with only the case's task and input. Do not show the
   assistant the expected checks.
3. Run the same task in the receiving setup with the intended skills and selected
   references loaded. Keep model/settings and source input aligned where possible;
   record unavoidable differences.
4. Save both outputs privately. Give them neutral labels and vary their order for
   review. Check the source text directly rather than judging resemblance to a
   preferred assistant's prose.
5. Record each expected check as `pass`, `fail`, or `not_assessable`, with a short
   output quotation or location supporting the judgment. Record critical failures
   separately from presentation preferences.
6. Fix the smallest relevant instruction, example, or tool defect. Repeat the
   affected cases. Use additional unseen documents before claiming useful transfer
   in the intended task setting.

基準組與移轉組應使用相同來源文字；法律意義、證據支持及格式偏好須分開評估。若模型或工具不同，應記錄差異，不可將所有變化都歸因於技能移轉。

## What to assess

| Area | Substantive checks | Separate presentation checks |
| --- | --- | --- |
| Translation | Parties, defined terms, obligations/permission, negation, conditions, exceptions, quantities, references, ambiguity | Requested language variant, alignment, numbering, readability |
| Legal sources | Source identity, pinpoint support, date/version, treatment-check limits, authority versus commentary | Clear authority table and labeled uncertainty |
| Study | Fidelity to the supplied packet, holding versus dissent, procedure and issue, no invented facts | Useful English/Traditional Chinese organization |
| Office extraction | Supported fields, source locations, missing/ambiguous values, requester versus counterparty | Valid requested schema and consistent date/language fields |
| Empirical review | Records versus studies, available text level, reporting limits, no fabricated appraisal | Clear evidence table and reproducible scope |

An initial release check should have no unresolved critical failures in these
fixtures. Passing them is a narrow regression result; it is not certification of
legal accuracy, professional competence, or performance on unseen work. Automated
or LLM-assisted scoring can help organize review, but should not silently become
the only evidence for substantive legal fidelity.

## Evidence and currentness

All source packets here are closed, fictional inputs. Source IDs such as
`LE-001-A` identify text inside `fixtures.json`; they are not citations to real
authority. For these cases, do not invent external citations or browse for a
fictional authority. A case asking about current law must receive the appropriate
verification limitation when its packet cannot establish current status.

On actual legal research, record the jurisdiction, applicable date, original
source, relevant version, pinpoint, and the scope/date of any subsequent-treatment
check. Bibliographic existence alone does not establish support or currentness.

## Keep a genuine holdout

These public fixtures are visible to developers and can enter model context.
They are regression examples, not an uncontaminated benchmark. For an operational
comparison, reserve authorized unseen documents or whole matter families outside
the shared repository. Splitting adjacent clauses from one agreement across
development and evaluation sets can leak terminology and context.

Do not commit confidential documents, account exports, personal memory, recipient
bindings, or model outputs containing private material. Publish only deliberately
reviewed aggregate findings or sanitized examples, with the relevant scope stated.
