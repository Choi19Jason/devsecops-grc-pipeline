# Health check: skip ZAP safely when the app is down

Added 2026-11-07, commit `38f5334` on `main`. Workflow: `.github/workflows/security-scan.yml`.

## Before
The ZAP job started the app in a container and waited up to 30 seconds for `/health`. If the app never answered, the step printed the container logs and exited 1, so the whole ZAP job failed. The Trivy and CodeQL jobs have no dependency on it, so they ran either way.

## After
- The health step has an id (`health`) and writes `healthy=true` or `healthy=false` to its output instead of failing.
- The ZAP scan step runs only when `healthy` is `true`.
- When the app is not healthy, the run shows a warning ("App did not answer /health in 30 seconds. ZAP baseline skipped.") and a line in the run summary. The ZAP job finishes green and the other jobs finish normally.
- A failed `docker build` still fails the job. A broken build is a real failure; an unhealthy app is a skip.
- Each job has a `timeout-minutes` limit (Trivy 20, CodeQL 30, ZAP 15; my own guesses, to adjust after more runs) so a hung job cannot run for hours.

## Evidence
| Run | What it tested | Result |
|---|---|---|
| #18 (branch `test-health-skip`, run by hand) | Health URL pointed at `/nope` on purpose | All three jobs green; summary says "ZAP baseline SKIPPED"; warning shown; no ZAP report uploaded; ZAP took 45 seconds |
| #19 (`main`, commit `38f5334`) | Normal app, real `/health` | All three jobs green; no skip warning; artifact `zap-baseline-report` (25.3 KB) uploaded |

## The security tradeoff
This makes the pipeline fail-open for ZAP: if the app is down, the scan is skipped and the run still passes, so code could ship without that scan. I made every skip visible (warning and summary) so it cannot happen silently. Whether a skipped scan should block a merge in a real pipeline is an open question; it is tracked as R-16 in `docs/risk-register-and-poam.md` and in POA&M item P-04.

## How this was built
The idea came from a mentoring conversation with an application security engineer. I applied the change with Claude Code's guidance (the assistant supplied the code and explained each step), tested it on a branch with a bad URL, and cherry-picked the tested commit onto `main`.

## Limits
- It covers only the ZAP job. A Trivy database download failure would still fail the Trivy job.
- Passive ZAP baseline only. The test used a deliberately bad health URL, not a real outage.
