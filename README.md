# devsecops-grc-pipeline

A small DevSecOps lab: a deliberately vulnerable Flask app, a GitHub Actions pipeline that scans it three ways, and a GRC layer that maps the pipeline to NIST SP 800-53.

> **Warning:** `app/` is intentionally vulnerable (SQL injection, reflected XSS, hardcoded secret, debug mode, outdated dependencies, root container). I planted every flaw myself so the scanners have something to find. Fictional data only. Do not deploy it.

## Status

Work in progress. Nothing below is claimed until it has run and the result is in this repo.

- [x] App, Dockerfile, and pipeline written
- [x] First pipeline run green on GitHub Actions (2026-10-28)
- [x] Baseline findings recorded (before counts): `docs/baseline-findings.md`
- [ ] 3 to 5 findings fixed and rescanned (after counts)
- [ ] NIST SP 800-53 mapping
- [ ] Architecture diagram

## What each tool does

| Stage | Tool | What it checks | Where results go |
|---|---|---|---|
| SCA, secrets, IaC, container image | Trivy (Aqua Security's open-source scanner) | Known CVEs in dependencies and the image, secrets, Dockerfile misconfiguration | GitHub Security tab (SARIF) |
| SAST | CodeQL | Flaws in the Python source code | GitHub Security tab |
| DAST (passive) | OWASP ZAP baseline | Missing security headers, cookie flags, information leaks on the running app | Workflow artifact (HTML, JSON, Markdown) |

## Honest limits

- This uses Trivy, the open-source scanner from Aqua Security. It does not use Aqua's commercial platform.
- ZAP baseline is passive: it does not attack the app, so it will not find the SQL injection. CodeQL covers that.
- The target is a toy app I wrote, not production code. Finding counts show that the pipeline works, not how secure a real system is.

## Supply-chain note

Every third-party action in `.github/workflows/security-scan.yml` is pinned to a full commit SHA instead of a tag. In March 2026 the `aquasecurity/trivy-action` version tags were force-pushed to malicious code; a pinned SHA cannot be moved that way.
