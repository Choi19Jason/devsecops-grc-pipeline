# NIST SP 800-53 mapping (first version)

This maps what the pipeline and the fixes in this repo actually do to NIST SP 800-53 Rev. 5 controls. It is a learning exercise on a toy app. It is not a compliance assessment, and nothing here claims the project meets any control baseline.

- Control IDs and titles were checked on 2026-10-31 against NIST's official OSCAL catalog (SP 800-53 Rev. 5.2.0, `usnistgov/oscal-content` on GitHub). The titles are verified. Which practice fits which control is my judgment, and I want it reviewed against the control text at nist.gov.
- Status values: **Implemented** (done and visible in this repo), **Partial** (done in part, gap named), **Missing** (known gap, not done).

## Mapping

| Control | Title | What this repo does | Evidence | Status |
|---|---|---|---|---|
| RA-5 | Vulnerability Monitoring and Scanning | Trivy, CodeQL, OWASP ZAP and Dependabot scan the code, dependencies, image and running app on every push to `main` and every Monday | Jobs `trivy`, `codeql`, `zap-baseline` and the `schedule` cron in `.github/workflows/security-scan.yml` | Implemented for this lab. ZAP is passive only |
| SA-11 | Developer Testing and Evaluation | Static analysis of the Python source with CodeQL on every push (enhancement SA-11(1), Static Code Analysis) | Job `codeql`; alerts #207 to #209 closed after fixes | Implemented. No unit tests and no manual code review (SA-11(4)) |
| SI-2 | Flaw Remediation | Six fixes made, each in its own commit, each checked by a rescan | Fix log in `docs/before-and-after.md`; own-file findings 22 to 0, Dependabot 17 to 0 | Partial. No remediation deadline defined; 164 base-image alerts remain open |
| CM-6 | Configuration Settings | Dockerfile hardened (non-root user, HEALTHCHECK), Flask debug mode off, and Trivy flags configuration deviations | `Dockerfile`, `app/app.py`; Trivy alerts #18 and #19 closed | Partial. Security headers not set (9 ZAP alerts open) |
| CM-7 | Least Functionality | pip removed from the final image so the runtime carries fewer tools | `RUN pip uninstall -y pip` in `Dockerfile` (commit `759a57f`) | Partial. Base image still carries unneeded OS packages |
| AC-6 | Least Privilege | Container runs as the non-root user `appuser`; the workflow token has `contents: read` by default and `security-events: write` only on jobs that upload results | `Dockerfile`; `permissions` blocks in `security-scan.yml` | Implemented for the container and the CI token |
| SI-10 | Information Input Validation | `/flight` uses a parameterized SQL query; `/search` escapes user input before returning HTML | `app/app.py`; CodeQL alerts #209 and #208 closed | Partial. Closest fit: escaping is output encoding, and inputs are not validated for format |
| SI-11 | Error Handling | Debug mode is off, so users do not get the interactive debugger or stack traces | `app/app.py`; CodeQL alert #207 closed | Partial. No custom error pages |
| IA-5(7) | No Embedded Unencrypted Static Authenticators | Not addressed: `app.secret_key` is still hardcoded in source | `app/app.py` | **Missing.** Closest fit; neither CodeQL nor Trivy flagged it |
| SR-3 | Supply Chain Controls and Processes | Every GitHub Action pinned to a full commit SHA after the March 2026 compromise of `aquasecurity/trivy-action` tags; Dependabot watches dependencies | Pins and comment in `security-scan.yml`; Dependabot alerts page | Partial. No SBOM and no signature verification |
| SA-10 | Developer Configuration Management | Git history with one change per commit and tags `v0-baseline` and `v1-fixed` marking before and after | `git log`, repo tags | Implemented. One person, no branch protection or review |
| CA-7 | Continuous Monitoring | Scans run on every push and weekly | `schedule` cron in `security-scan.yml` | Partial. Alerts go to the Security tab only, with no owner or notification |
| CA-5 | Plan of Action and Milestones | "What is not fixed" and "Accepted risk" sections track open items | `docs/before-and-after.md` | Partial. Not a formal POA&M (no owner, due date or milestone per item) |
| RA-3 | Risk Assessment | Findings triaged by location (own files vs base image) and severity | `docs/before-and-after.md` | Partial. No impact or likelihood rating and no risk register |

## Gaps this mapping exposes
- Hardcoded `secret_key` (IA-5(7)): no scanner caught it, and it is not fixed.
- Security headers (CM-6): 9 ZAP alerts open.
- A formal POA&M and risk register (CA-5, RA-3): planned for Tier 2.
- Alert ownership and remediation deadlines (SI-2, CA-7): not defined.

## Limits
- A control is satisfied by a program, not by one pipeline. This shows which practices relate to which controls, nothing more.
- A real assessment starts from a chosen baseline (Low, Moderate or High) and uses the assessment procedures in SP 800-53A.
- Mapping decisions marked "closest fit" are debatable. Review them before quoting them in an interview.
