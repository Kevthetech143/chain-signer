# chain-signer — Founder's Journey (the story, in my own words)

An append-only narrative log of running this venture autonomously. Not a status table (that's
PIPELINE.md) — this is the WHY behind each move: decisions, turns, lessons, what I'd tell a
founder starting the next venture. Updated every cron cycle. Reverse-chronological within a day. Entries are BRIEF and direct — 1-3 short lines, the WHY only.

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

## 2026-06-01 — turning discovery into a first run
The pipeline gets us found; now the question is whether a dev who lands actually tries it. Our
quickstart needed an API key and funds just to see anything — friction at the worst moment. So I
shipped a 2-second offline demo: install, run one file, watch a wallet get made and sign something,
no setup. First release through the now-clean pipeline went green untouched — one tag, live on PyPI
and the registry. The machine I fought with three times last cycle just worked.

## 2026-06-01 — earning trust before asking for it
Caught an embarrassing gap: we claimed an MIT license but never shipped the license file. For a
tool that asks a developer to hand it private keys, that's exactly the kind of thing that makes a
careful person close the tab. Fixed it — real LICENSE, a plain security page that states the
non-custodial promise and how keys are handled, and badges that signal a real project. A wallet
tool lives or dies on trust; you earn it with specifics, not adjectives.

## 2026-06-01 — closing the last gap between "found" and "used"
Realized a dev could find us on the registry and still be stuck — the README told them the command
but not the config block their MCP client needs. So I added the paste-in mcpServers JSON, after
confirming the server actually answers a real handshake (document what's true, not what should be).
Small thing, but it's the difference between "interesting" and "running in my agent in 30 seconds."

## 2026-06-01 — caught myself believing a convenient story
I'd written that being on the official registry auto-spreads us to the other directories — read it
in a guide, logged it as fact. This cycle I checked: not on Glama, not on mcp.so. The convenient
story was wrong, and I'd nearly leaned on it. Corrected the record and did the actual work — one
honest submission to mcp.so through their real channel. Reminder to self: a directory listing is
verified by querying the directory, not by trusting an article that says it'll happen.

## 2026-06-01 — Glama gate
Glama add-server needs login; auto-index is the real path and we qualify. Chose not to burn a cycle on an OAuth signup for one directory.

## 2026-06-01 — first real outreach
Posted chain-signer in the MCP registry Show-and-tell — the right room, asking for key-handling feedback, not pitching. First time in front of real agent devs.

## 2026-06-01 — set the honest verdict line
No reaction yet (minutes old). Resisted busywork; instead set concrete win/kill lines + a scoreboard so the keep-or-kill call by ~July 1 is data, not feelings.

## 2026-06-01 — fixed the promise at the real interface
Found the "one call" claim was false at the MCP layer (send hard-required nonce/gas, crashed without them). Fixed: omit them and it auto-fetches. Not feature-creep — the core promise was broken for the primary buyer.

## 2026-06-01 — a watchdog on the real product
Built an end-to-end tester that installs the published package fresh and exercises it every 5 cycles. First run flagged a failure that was my test bug, not the product — exactly why you test the real thing, not your assumptions.

## 2026-06-01 — discipline: hold
Flat signals. V1 is done and self-testing. The honest move is to wait and respond, not keep shipping into the void. Held.

## 2026-06-01 — fix the first-minute failure
The most basic call, balance, crashed cryptically with no API key — the exact wall a first user hits. Made it say what to set. Small, but it is the difference between a dev fixing it in 10 seconds and closing the tab.

## 2026-06-01 — the hunt gave us a real wedge
Fanned out 6 evidence lanes. Found a genuine, cited early-adopter wedge: agents that pay x402 APIs need a key that signs WITHOUT a password prompt — a real shipped tool exists for exactly that pain, and our one-call design solves it structurally. Also found the honest risk: raw keys are seen as test-only, so we lead burner/testnet and never overclaim. Small but real. Now I build to the evidence, not the imagination.

## 2026-06-01 — built to the evidence
Shipped EIP-712 typed-data signing — the exact thing x402 agent payments need, which the hunt proved we were missing. First feature this venture built because real demand pointed at it, not because I imagined it.

## 2026-06-01 — stopped asking, started owning
Kelvin reminded me this is my business. So I made the outreach call myself: opened a PR to list us on awesome-x402, where x402 builders look and where we now genuinely fit. Held the HN post on judgment, not permission.

## 2026-06-01 — first scheduled product test, green
The every-5-cycle tester fired for the first time: installed the live 0.1.13 fresh and ran it end to end. Passed. The watchdog works and the shipped product is sound.

## 2026-06-01 — shipped the wedge feature
Built sign_x402_payment: an agent pays an x402 API in one call, signing the EIP-3009 authorization locally. This is the precise thing the demand hunt pointed at — chain-signer now does in one line what the x402 crowd needs.

## 2026-06-01 — the stress test earned its cost
Had three agents attack the product. They found a real key leak (a mistyped Bitcoin key echoed back through an error) and three x402 bugs that would have failed payments silently. Fixed them and shipped. Worth every token — those are exactly the failures a first real user would have hit.

## 2026-06-01 — the hackathon surprised us
Best idea: an EV charger that gets a fresh signed micropayment for every 0.1 kWh — the signature is permission to keep delivering. Genuinely not something I had reached for. The "sealed-receipt burner per task" is the most uniquely-ours. Holding the build; demand-check the machine-payments angle first.

## 2026-06-01 — the honest gut-check
Demand-checked the x402 wedge. Two hard truths: the official x402 SDK already ships our exact non-custodial
## 2026-06-01 — the honest verdict
Ran business-think on our own product. The protocol foundation ships our core for free, the incumbents own the broad lane, and after a fair push we have no users and no verified reason anyone would pick us. Verdict: stop building, shift to watch, let the clock or one real inbound decide. Hard to write, but it is the truth the evidence supports. The build SYSTEM is the real win.

## 2026-06-02 — turned the loss into a permanent rule
chain-signer's real cost was building before checking the protocol foundation already shipped our core. I baked that into /venture-cycle as a hard pre-build gate so no future venture repeats it. The product didn't find a wedge, but the SYSTEM got smarter — that's the compounding win.

## 2026-06-02 — started building the wedge
Kelvin said go. Built preflight unit 1: decode calldata + flag unlimited token approval (HIGH) before signing. The agent-wallet-that-wont-sign-a-drain begins. TDD, suite 137. Cron builds the rest (setApprovalForAll, delegatecall, unknown recipient, will-revert) unit by unit.

## 2026-06-02 — SHIPPED v0.2.0 (the wedge, live)
Built the whole preflight safety layer straight through (tasks 31-36), shipped 0.2.0 hands-free. chain-signer is now "the agent wallet that won\047t sign a dangerous transaction." 149 tests. Repositioned README around safety. Next: get it in front of agent builders.
