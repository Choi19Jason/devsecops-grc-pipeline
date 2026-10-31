# Before and after

- Before: tag `v0-baseline` (commit `049df1e`, scanned 2026-10-28)
- After: tag `v1-fixed` (commit `759a57f`, scanned 2026-10-30)
- Counts come from the GitHub Security tab filters (`is:open branch:main ...`) and the Dependabot alerts page.

## Counts

| Source | Before | After | Change |
|---|---|---|---|
| CodeQL (app code) | 3 | 0 | -3 |
| Trivy, `app/requirements.txt` | 17 | 0 | -17 |
| Trivy, `Dockerfile` | 2 | 0 | -2 |
| Trivy, built image | 187 | 164 | -23 |
| **Trivy total** | **206** | **164** | **-42** |
| Trivy by severity (critical / high / medium / low) | 0 / 58 / 80 / 68 | 0 / 44 / 58 / 62 | |
| **Code scanning total (CodeQL + Trivy)** | **209** | **164** | **-45** |
| Dependabot alerts | 17 | 0 | -17 |
| OWASP ZAP baseline alerts | 9 | not remediated, not re-recorded | |

Findings in the files I own (app code, `requirements.txt`, `Dockerfile`): 22 before, 0 after.

The remaining 164 open alerts are all Trivy findings in the built image. Every row I reviewed is a Debian operating-system package in the `python:3.12-slim` base image (for example util-linux, tar, perl, ncurses, zlib). I did not plant them and my fixes cannot close them. See "Accepted risk" below.

## Fix log

| Fix | Commit | Proof |
|---|---|---|
| 1. SQL injection: parameterized query in `/flight` | `900bd32` | CodeQL alert #209 closed as fixed |
| 2. Reflected XSS: `html.escape` in `/search` | `0b68cda` | CodeQL alert #208 closed as fixed |
| 3. Flask debug mode off, bind to localhost by default | `96166c9` | CodeQL alert #207 closed as fixed |
| 4. Updated Flask, Werkzeug, Jinja2 and other pins | `2f5e9ce` | 17 Trivy alerts (`requirements.txt`) and 17 Dependabot alerts closed |
| 5. Dockerfile: non-root user, HEALTHCHECK, newer pip | `8a45aaa` | Trivy alerts #18 (root user) and #19 (no HEALTHCHECK) closed |
| 6. Remove pip from the final image | `759a57f` | About 8 new alerts closed (see below) |

## A fix that created new findings
Fix 5 upgraded pip. The newer pip bundles its own copies of urllib3, msgpack and setuptools, and Trivy flagged them: about 8 new alerts appeared (numbers #210 to #216 identified). Those libraries are build tools the app never uses at runtime. Fix 6 removed pip from the final image. The arithmetic fits: 214 Trivy alerts were ever opened (206 plus 8 new), 164 are open, and all 164 are original baseline image alerts.

## What is not fixed
- **Hardcoded `secret_key` in `app/app.py`.** Neither CodeQL nor Trivy flagged it, so no scanner proves a fix. This is a detection gap. The fix is to read the key from an environment variable.
- **ZAP baseline alerts (9).** Missing security headers (CSP, anti-clickjacking, nosniff, and others). Not addressed in this sprint.
- **Base-image OS packages (164).** See below.

## Accepted risk (base image)
The 164 open Trivy alerts are in the operating-system layer of the official `python:3.12-slim` image. Decision: accept and document them for this lab instead of hiding them, so the before and after numbers stay comparable. Still to check: how many have a vendor fix available (the Trivy alert page shows a fixed version when there is one). A production decision would be a smaller base image or a rebuild cadence that picks up patched packages.

## Limits
- Counts depend on Trivy's database and the base image on the scan date. A rerun next week can differ without any code change.
- ZAP baseline is passive, so "not flagged" does not mean "not vulnerable".
- Single toy app. These numbers show that the pipeline works, not how secure real software is.
