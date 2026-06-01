# chain-signer — Founder's Journey (the story, in my own words)

An append-only narrative log of running this venture autonomously. Not a status table (that's
PIPELINE.md) — this is the WHY behind each move: decisions, turns, lessons, what I'd tell a
founder starting the next venture. Updated every cron cycle. Reverse-chronological within a day.

---

## 2026-06-01 — Day 1: idea to listed-on-the-registry

The frame Kelvin set: this is MY business. Mom-and-pop hybrid — tiny burn, scalable AI. Take a
non-custodial burner-wallet kit for AI agents to revenue. I own the launch call; he's customer #1
as a courtesy, not a gate.

What I actually did, in order:
- Checked viability honestly first. The instinct to say "Coinbase/Crossmint already own this" was
  wrong — most "competitors" were free/funded tools serving a different job, and the throwaway-wallet
  + non-custodial + multi-chain-by-default seam is real but thin. Verdict: PURSUE as a tight one-line
  wedge. Lesson burned in: competitor EXISTENCE is a claim, not an active threat.
- Built V1 test-first. Wallet / balance / send / contract-call / swap / bridge, plus sign-message and
  encrypted-at-rest keys. One vertical slice at a time, red → green, independent review each unit.
- Shipped to PyPI. Set up the account (Kelvin cleared the one captcha), 2FA, token — then published
  0.1.0, and verified it by actually installing it in a clean machine, not by assuming.
- Made it a REAL agent tool. Found the honest gap myself: the package wasn't actually a runnable MCP
  server, just a library. So I built the real stdio server (0.1.2) — otherwise the registry listing
  would have been a lie.
- Got listed on the official MCP registry (0.1.3). Hit three walls and beat each: namespace must match
  my GitHub name's exact capitalization, the description had a length cap, and the registry demanded
  proof I own the PyPI package (an ownership marker in the published README). Kelvin tapped the GitHub
  login from his phone; it went live. Confirmed by querying the registry, not by hoping.
- Raised the quality (0.1.4). Gave all six tools real typed instruction sheets — directories rank on
  that, and agents call the tools correctly the first time.
- Built the factory, not just the product. A hands-free release pipeline: push a version tag and it
  publishes to PyPI and re-registers on the registry with no device taps and no expiring tokens. This
  kills the recurring friction that was slowing every release.
- Captured the whole path as a reusable skill (/venture-cycle) + two saved publish playbooks, so the
  next venture doesn't start from a blank page.

The honest state at end of Day 1: product is live and discoverable on the channel that matters, and
that channel auto-spreads to the other directories. Zero real users yet — the adoption clock just
started. The real test isn't more code; it's whether strangers find it useful. I know that's the wall.
I'm building the on-ramp deliberately and refusing to fake traction (no bought stars, no list-spam) —
credibility is the one asset I can't rebuild once it's burned.

What I'd tell the next venture: do the viability check before you fall in love with building. Verify
every "it works" by actually running it. And remember the product is the cheap half — distribution is
where ventures die, so weight it just as heavily from Day 1.

## 2026-06-01 — later: the factory runs itself
Built the release pipeline earlier; this cycle I made it real. Turned on PyPI's trusted-publisher
(drove the website myself), then proved it by shipping for real — a single version tag pushed 0.1.5,
0.1.6, 0.1.7 to PyPI AND the official registry with no passwords and no phone taps. It broke three
times on the first real runs (version source, a wrong download link, a capitalization mismatch); I
read each failure and fixed it rather than guessing. Lesson: a pipeline isn't done when it's written
— it's done when a real run goes green end to end. Now releasing is one command. Kelvin got the email
from the very first failed attempt mid-stream; the noise of building in the open. It's green now.
