# DevSecOps + GRC Pipeline: Automated Security Scanning and NIST 800-53 Mapping

[![security-scan](https://github.com/Choi19Jason/devsecops-grc-pipeline/actions/workflows/security-scan.yml/badge.svg)](https://github.com/Choi19Jason/devsecops-grc-pipeline/actions/workflows/security-scan.yml)
![status](https://img.shields.io/badge/status-active-brightgreen)
![fixes](https://img.shields.io/badge/fixes-7%20made-blue)
![scanners](https://img.shields.io/badge/scanners-Trivy%20%7C%20CodeQL%20%7C%20ZAP%20%7C%20Dependabot-6f42c1)
![NIST](https://img.shields.io/badge/NIST%20800--53-14%20controls%20mapped-orange)

A small DevSecOps lab: a Flask app I wrote with security flaws planted on purpose, a GitHub Actions pipeline that scans it four ways, and a GRC layer that maps the pipeline to NIST SP 800-53. The loop is **scan, triage, fix, rescan, document**.

**Author:** Joonwoo "Jason" Choi, CIT at Purdue (Class of 2028), targeting Summer 2027 AppSec, GRC and security internships.

## TL;DR (what a reviewer should take away)

- Built a **GitHub Actions** pipeline that runs **Trivy** (Aqua Security's open-source scanner), **CodeQL** (SAST) and **OWASP ZAP** (passive DAST) on every push and every Monday, with **Dependabot** watching the dependencies. Results go to the GitHub Security tab.
- Fixed all **22 scanner-reported findings in my own files** (SQL injection, reflected XSS, debug mode, 17 outdated libraries, a root container) and proved each fix with a rescan. **Dependabot went from 17 to 0** and **CodeQL from 3 to 0**.
- Found that **one of my own fixes made things worse**: upgrading pip added about 8 new alerts from pip's bundled libraries. I traced them and removed pip from the final image.
- Recorded what the scanners **missed**: CodeQL and Trivy both skipped a hardcoded secret key (fixed by hand in Fix 7), and passive ZAP does not test for injection.
- Mapped the pipeline to **14 NIST SP 800-53 Rev. 5 controls** with evidence, status and gaps.
- Pinned every third-party Action to a commit SHA after the March 2026 compromise of the Trivy action's version tags.

**Start here:** [Before and after](docs/before-and-after.md) · [Baseline findings](docs/baseline-findings.md) · [NIST 800-53 mapping](docs/nist-800-53-mapping.md) · [Workflow](.github/workflows/security-scan.yml)

> **About the flaws:** `v0-baseline` is the app with the flaws I planted (SQL injection, reflected XSS, hardcoded secret, debug mode, outdated dependencies, root container) so the scanners had something known to find. `main` has the fixes. Fictional data only. This is a lab app, not production software, so do not deploy it.

## Results

Scanned at tag `v0-baseline` (2026-10-28) and again at `v1-fixed` (2026-10-30). Details and fix log: [docs/before-and-after.md](docs/before-and-after.md).

| Source | Before | After |
|---|---|---|
| CodeQL (app code) | 3 | 0 |
| Trivy, my own files (`requirements.txt`, `Dockerfile`) | 19 | 0 |
| Dependabot | 17 | 0 |
| Trivy, built image | 187 | 164 |
| Code scanning total (CodeQL + Trivy) | 209 | 164 |

The 164 that remain are operating-system packages in the base image, which I did not plant and treat as accepted risk for this lab. Fix 7 (the hardcoded `secret_key`, commit `930deb9`) came after the `v1-fixed` scan. No scanner flagged that flaw, so it is proven by reading the code, not by a closed alert. Not fixed: the 9 ZAP header alerts.

## Architecture

![Architecture of the devsecops-grc-pipeline: your PC pushes to GitHub, GitHub Actions runs Trivy, CodeQL and OWASP ZAP while Dependabot watches the dependency list, findings land in the Security tab, a ZAP report and Dependabot alerts, then feed triage and fixes, which loop back to your PC and feed the GRC layer.](docs/architecture.svg)

A change is pushed to GitHub, the three scan jobs run in GitHub Actions, and their findings land in the Security tab (Trivy, CodeQL), a downloadable artifact (ZAP) and Dependabot alerts. I triage the findings, fix the code, and push again. The GRC layer maps the controls this loop exercises to NIST SP 800-53.

## Status

- [x] App, Dockerfile, and pipeline written
- [x] First pipeline run green on GitHub Actions (2026-10-28)
- [x] Baseline findings recorded (before counts): [docs/baseline-findings.md](docs/baseline-findings.md)
- [x] Fixes made and rescanned, after counts recorded (6 fixes plus Fix 7 for the secret key): [docs/before-and-after.md](docs/before-and-after.md)
- [x] NIST SP 800-53 mapping, first version (control titles verified, judgments under review): [docs/nist-800-53-mapping.md](docs/nist-800-53-mapping.md)
- [x] Architecture diagram
- [ ] Next: SonarQube beside CodeQL, a risk register and POA&M, security headers for the ZAP alerts, an API test against the OWASP API Top 10

## What each tool does

| Stage | Tool | What it checks | Where results go |
|---|---|---|---|
| SCA, secrets, IaC, container image | Trivy (Aqua Security's open-source scanner) | Known CVEs in dependencies and the image, secrets, Dockerfile misconfiguration | GitHub Security tab (SARIF) |
| SAST | CodeQL | Flaws in the Python source code | GitHub Security tab |
| DAST (passive) | OWASP ZAP baseline | Missing security headers, cookie flags, information leaks on the running app | Workflow artifact (HTML, JSON, Markdown) |
| SCA | Dependabot | Outdated or vulnerable libraries in `requirements.txt` | Dependabot alerts page |

## What I learned

- **A fix can create new findings.** The pip upgrade added alerts; re-scanning after every fix is what caught it.
- **No single scanner caught everything.** The detection table is in [docs/baseline-findings.md](docs/baseline-findings.md).
- **Counts mislead without context.** 209 to 164 sounds small. Most of the 164 are base-image packages my fixes cannot close, and in my own files the count went from 22 to 0.

## Honest limits

- This uses Trivy, the open-source scanner from Aqua Security. It does not use Aqua's commercial platform. I have not used SonarQube, Jira, XBOW or Traceable.
- ZAP baseline is passive: it does not attack the app, so it will not find the SQL injection. CodeQL covers that.
- The target is a toy app I wrote, not production code. Finding counts show that the pipeline works, not how secure a real system is.
- The NIST mapping is a learning exercise, not a compliance assessment. Rows marked "closest fit" are debatable.

## How I built this

I am new to application security and used Claude Code (an AI coding assistant) as a mentor and pair programmer. I created the repo, made and pushed the commits, and ran the scans and checked the results in the Security tab. Fixes 1, 2, 3 and 7 are code I typed myself while the assistant explained them; the assistant wrote the first versions of the app, workflow and other files and drafts of the docs, which I reviewed before committing.

## Supply-chain note

Every third-party action in `.github/workflows/security-scan.yml` is pinned to a full commit SHA instead of a tag. In March 2026 the `aquasecurity/trivy-action` version tags were force-pushed to malicious code; a pinned SHA cannot be moved that way.
