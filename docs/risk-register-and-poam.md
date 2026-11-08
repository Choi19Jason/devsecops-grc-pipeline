# Risk register and POA&M (first version)

Written 2026-11-01. This turns the scan findings in this repo into two standard GRC records: a **risk register** (what could go wrong, how bad, and what I decided to do about it) and a **POA&M** (Plan of Action and Milestones: who fixes each open item, what the steps are, and by when).

This is a learning exercise on a toy app. It is not a formal risk assessment, and nothing here claims the project meets any control baseline.

- **Who owns everything:** me (Jason). There is no team, no real asset owner and no real business impact.
- **Ratings are my judgment.** I scored each risk as if the app were a small internal web app holding non-sensitive data. I did not assess exploitability CVE by CVE.
- **Dates are my own targets**, not commitments to anyone else.
- **Method:** a simplified qualitative approach in the spirit of NIST SP 800-30 Rev. 1. Likelihood (L) and Impact (I) are each rated 1 (low), 2 (medium) or 3 (high). Score = L x I. Score 1 to 2 = **Low**, 3 to 4 = **Medium**, 6 to 9 = **High**.
- **Evidence:** findings come from `docs/baseline-findings.md`, `docs/before-and-after.md` and `docs/evidence/zap-baseline-report-2026-10-28.md`. NIST control IDs match `docs/nist-800-53-mapping.md`.

## 1. Open risks

| ID | Risk | Evidence | L | I | Score | Rating | Treatment | Status |
|---|---|---|---|---|---|---|---|---|
| R-08 | Operating-system packages in the `python:3.12-slim` base image carry known CVEs, and the count rises as new CVEs are published | Trivy: 164 open at `v1-fixed` (44 High, 58 Medium, 62 Low); 177 open on 2026-11-01 (alerts #218 to #230 are new); all in `library/flightdesk:1` | 2 | 2 | 4 | Medium | Mitigate in part (P-01), accept the rest | Open |
| R-09 | No Content-Security-Policy and no anti-clickjacking header, so the browser has no second layer if an injection flaw returns, and pages can be framed | ZAP baseline: 2 Medium alerts (CSP not set, 4 instances; anti-clickjacking, 1) | 2 | 2 | 4 | Medium | Mitigate (P-02) | Open |
| R-10 | Other hardening headers missing: `X-Content-Type-Options`, Permissions-Policy, and the Cross-Origin Embedder, Opener and Resource policies | ZAP baseline: 5 Low alerts | 2 | 1 | 2 | Low | Mitigate (P-02) | Open |
| R-11 | The `Server` header leaks the server and Python version, which helps an attacker pick known exploits | ZAP baseline: 1 Low alert, 5 instances. Evidence at baseline: `Werkzeug/2.2.2 Python/3.12.16` | 2 | 1 | 2 | Low | Mitigate (P-02) | Open |
| R-12 | Responses can be stored by shared caches | ZAP baseline: 1 Informational alert, 5 instances. The app serves only fictional data | 1 | 1 | 1 | Low | Mitigate with a `Cache-Control` header (P-02) | Open |
| R-13 | Detection gaps: the scanners miss some flaw types, so a flaw can sit unseen | `docs/baseline-findings.md`: CodeQL and Trivy missed the hardcoded secret key; passive ZAP sends no payloads, so it does not test injection | 2 | 2 | 4 | Medium | Mitigate (P-03) | Open |
| R-14 | No governance around findings: no branch protection or required review, no alert notification, no remediation deadlines | NIST mapping rows SA-10, CA-7, SI-2 (marked Partial) | 2 | 1 | 2 | Low | Mitigate (P-04) | Open |
| R-15 | No software bill of materials (SBOM) and no image signature check, so I cannot list or verify exactly what the image contains | NIST mapping row SR-3 (Partial) | 1 | 2 | 2 | Low | Mitigate (P-05) | Open |

## 2. Closed risks (kept as evidence)

| ID | Risk | Fix and proof | Rating before the fix | Residual risk |
|---|---|---|---|---|
| R-01 | SQL injection in `/flight` | Fix 1, commit `900bd32` (parameterized query); CodeQL alert #209 closed | High | Low. Inputs are still not validated for format |
| R-02 | Reflected XSS in `/search` | Fix 2, commit `0b68cda` (`html.escape`); CodeQL alert #208 closed | High | Low. No CSP yet (see R-09) |
| R-03 | Flask debug mode on, and the app listened on all interfaces | Fix 3, commit `96166c9`; CodeQL alert #207 closed | High | Low |
| R-04 | Hardcoded `secret_key` | Fix 7, commit `930deb9` (read from `FLASK_SECRET_KEY`, random per-start fallback). No scanner flagged the original, so the proof is the diff, not a closed alert | Medium | Low. No secrets manager; each container start uses a new random key |
| R-05 | 17 outdated libraries with known CVEs | Fix 4, commit `2f5e9ce`; 17 Trivy alerts and 17 Dependabot alerts closed | Medium | Low |
| R-06 | Container ran as root and had no HEALTHCHECK | Fix 5, commit `8a45aaa`; Trivy alerts #18 and #19 closed | Medium | Low |
| R-07 | The Fix 5 pip upgrade added about 8 new alerts from pip's bundled libraries | Fix 6, commit `759a57f` (pip removed from the final image) | Low | Low |

## 3. POA&M (open items)

Status key: Not started, In progress, Done. All dates are my own targets. Today is 2026-11-01.

| ID | Risks | Weakness | Related NIST controls | Milestones (what I will do) | Resources | Owner | Target date | Status |
|---|---|---|---|---|---|---|---|---|
| P-01 | R-08 | Base-image OS packages with known CVEs; floating image tag lets the count move without a code change | SI-2, RA-5, CM-6 | 1. Pin the base image to a digest in the `Dockerfile`. 2. Rebuild and rescan; record the count with its date. 3. Open a sample of alerts and note how many have a vendor fix. 4. Decide per alert group: patch by rebuilding or accept. 5. Document the rebuild cadence (weekly cron already exists) | Docker Hub image digest; Trivy alert pages | Jason | 2026-11-04 | Not started |
| P-02 | R-09, R-10, R-11, R-12 | Missing security headers, version leak, cacheable responses | CM-6, SI-2 | 1. Add the headers in the Flask app: Content-Security-Policy, frame protection, `X-Content-Type-Options: nosniff`, Permissions-Policy, Cross-Origin-Opener, Embedder and Resource policies, `Cache-Control`. 2. Suppress or genericize the `Server` header (may need a change to how the app is served). 3. Rerun the ZAP baseline and record the after count. 4. Update the mapping row for CM-6 | Flask docs, OWASP Secure Headers guidance, ZAP baseline job | Jason | 2026-11-05 | Not started |
| P-03 | R-13 | Scanners miss some flaw types | SA-11, RA-5 | 1. Add SonarQube Cloud beside CodeQL and compare results on the same app. 2. Consider a ZAP full scan against my own local container only, never a third-party site. 3. Update the detection table in `docs/baseline-findings.md` with the new tool columns | SonarQube Cloud free tier (needs an account I create), ZAP | Jason | 2026-11-08 | Not started |
| P-04 | R-14 | No branch protection, no alert owner, notification or deadline | SA-10, CA-7, SI-2 | 1. Turn on branch protection for `main` (require pull requests and passing scan jobs). 2. Turn on email notifications for new alerts. 3. Write remediation targets: Critical 7 days, High 30, Medium 90, Low best effort (my own lab targets, not an industry standard) | GitHub repository settings | Jason | 2026-11-08 | Not started |
| P-05 | R-15 | No SBOM and no image signing | SR-3 | 1. Have Trivy generate a CycloneDX SBOM and keep it as a workflow artifact. 2. Note image signing (for example Sigstore cosign) as a later step | Trivy | Jason | 2026-11-15 | Not started |

## 4. Review log

| Date | What changed |
|---|---|
| 2026-11-01 | First version. 15 risks recorded: 7 closed, 8 open, tracked by 5 POA&M items |

Next review: 2026-11-08, or sooner if a weekly scan shows new alerts.

## 5. Limits
- A real risk register has a risk owner who is not also the person doing the work, a defined asset value, and management sign-off. This one has none of those.
- Likelihood and impact are my estimates on a lab app. Different reviewers could score them differently, and a CVE-by-CVE exploitability review of the 177 base-image alerts has not been done.
- Closing an item means I changed the file and the scan or diff confirms it. It does not mean the system is secure.
- The POA&M columns follow the usual fields (weakness, controls, milestones, resources, owner, date, status). It is not a document prepared for a formal authorization package.
