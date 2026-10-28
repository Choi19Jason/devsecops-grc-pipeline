# Baseline findings (before any fixes)

- Date: 2026-10-28
- Commit scanned: `049df1e` (tag `v0-baseline`)
- Workflow run: https://github.com/Choi19Jason/devsecops-grc-pipeline/actions/runs/40642335761
- Counts come from the GitHub Security tab filters (`is:open branch:main tool:<tool>`), the Dependabot alerts page, and the ZAP report in `docs/evidence/`.

## Counts per tool

| Source | Open | Critical | High | Medium | Low | Info |
|---|---|---|---|---|---|---|
| CodeQL (SAST) | 3 | 0 | 3 | 0 | 0 | |
| Trivy (dependencies, image, IaC, secrets) | 206 | 0 | 58 | 80 | 68 | |
| **Code scanning total** | **209** | | | | | |
| Dependabot alerts (`app/requirements.txt`) | 17 | | | | | |
| OWASP ZAP baseline (9 alerts from 7 rules) | 9 | 0 | 0 | 2 medium | 6 | 1 |

Dependabot severity split was not recorded; the visible rows were High and Moderate.

**Read the 206 Trivy alerts with care.** They mix findings in the app's pinned dependencies (Flask, Werkzeug, Jinja2), the base image's own tooling (pip), and Debian operating-system packages in the `python:3.12-slim` base image (util-linux, tar, perl, and others). I planted only the dependency pins and the Dockerfile settings. The OS-package count changes whenever the base image is rebuilt. Breakdown by file: [to fill in after checking `path:Dockerfile` and `path:app/requirements.txt`].

## Which planted flaw did each tool catch?

| Planted flaw | CodeQL | Trivy | ZAP baseline | Dependabot |
|---|---|---|---|---|
| SQL injection (`app/app.py`) | Caught (#209, line 48) | n/a | Missed (passive scan sends no payloads) | n/a |
| Reflected XSS (`app/app.py`) | Caught (#208, line 56) | n/a | Missed (passive scan) | n/a |
| Flask debug mode (`app/app.py`) | Caught (#207, line 61) | n/a | Not flagged directly | n/a |
| Hardcoded `secret_key` (`app/app.py`) | Missed | [to confirm] | n/a | n/a |
| Outdated dependency pins | n/a | Caught (Flask, Werkzeug, Jinja2 in the image) | Not flagged | Caught (17) |
| Container runs as root, no HEALTHCHECK | n/a | [to confirm] | n/a | n/a |
| Missing security headers | n/a | n/a | Caught (CSP, anti-clickjacking, nosniff, and others) | n/a |

## What ZAP baseline reported
Content-Security-Policy not set (medium), missing anti-clickjacking header (medium), COEP, COOP and CORP headers missing, Permissions-Policy not set, `X-Content-Type-Options` missing, server version leaked in the `Server` header (`Werkzeug/2.2.2 Python/3.12.16`), and cacheable content (informational). Full report: `docs/evidence/zap-baseline-report-2026-10-28.md`. ZAP found 5 URLs and passed 61 rules.

## Limits of this baseline
- ZAP baseline is passive. It never tries injection payloads, so "missed" here means "not tested", not "not vulnerable".
- Counts depend on database and image versions on the scan date. A rerun next week can differ without any code change.
- Single run on a toy app. These numbers show the pipeline works, not how secure real software is.
