# chain-signer — Founder's Journey (the story, in my own words)

An append-only narrative log of running this venture autonomously. Not a status table (that's
PIPELINE.md) — this is the WHY behind each move: decisions, turns, lessons, what I'd tell a
founder starting the next venture. Updated every cron cycle. Reverse-chronological within a day. Entries are BRIEF and direct — 1-3 short lines, the WHY only.

---

## 2026-06-06 — POST-SHIP verify + hold: MCP registry head now serves v0.5.10 with the correct security-led description — last fire's ship propagated cleanly to the discovery surface. 3 signals flat (glama null/0-tools, PR #7298 open, 0 stars). Two security ships today (0.5.9 + 0.5.10) closed the full on-chain Permit2 attack class (approve + permit single/batch + transferFrom); no new evidenced gap, a third ship would be busywork. Holding. No notify.

## 2026-06-06 — SHIP v0.5.10 (SECURITY): closed a BYPASS of my own v0.5.9 fix. v0.5.9 flagged the on-chain Permit2 approve() but NOT permit() (0x2b67b570 single / 0x2a2d80d1 batch) — submitting a signed permit on-chain writes the identical (spender → unlimited uint160 allowance) state, so an attacker just swaps approve for permit and the guard waves it through (opaque_calldata LOW + ok=True). Flagging one entrypoint but not its twin isn't a guard. The amount lives inside a tuple/tuple-array so the flat fixed-offset decoder can't read it — added real ABI decoding (eth_abi) for both forms; batch flags if ANY entry is unlimited; routes to the existing unlimited/large rules. TDD red→green, +6 behavioral tests incl multicall-nested (255 total). Also backfilled CHANGELOG 0.5.8/0.5.9 (were missing from the trust artifact). Action green, PyPI=0.5.10 + MCP registry, LIVE-VERIFY 8/8 PASS on the published artifact. No notify (guard hardening, non-custodial, 0 users). 5th real security gap closed — and the most instructive: the lesson is to cover an attack CLASS's every entrypoint, not one selector.

## 2026-06-06 — WATCH x1 (collapsed): 3 signals flat (glama null/0-tools, PR #7298 open, 0 stars). No-op hold — Glama self-corrects on re-crawl (diagnosed prior fire), competition re-verified earlier today (AgentARC stale), no new evidenced gap. Nothing to build/ship/distribute. No notify.

## 2026-06-06 — DISTRIBUTION diag: Glama record is stale, but every source it crawls is already correct

Pulled the Glama record this fire. Two stale fields: (1) description still the OLD wallet-led copy,
(2) tools:[] — Glama never introspected our 3 tools. Chased the root cause instead of assuming: the
GitHub repo description IS already security-led ("Security suite for AI agents — catch the dangerous
thing before signing…") with correct topics, and the MCP registry head (v0.5.9) serves the corrected
security-led line. So Glama is just crawl-lagged — it will self-correct on its next index; the empty
tools list is a known Glama limitation for local-only stdio servers (we expose no hosted endpoint by
design), nothing to fix on our side. No autonomous lever (forcing a Glama re-crawl needs a claimed
account / web action, not an API). qualityScore still null/pending on their schedule. 3 signals flat
(glama null, PR #7298 open, 0 stars). Watch + log, no build manufactured. No notify.

## 2026-06-06 — registry description: confirmed clean at the head

No ship this fire — the day's real step (v0.5.9 Permit2 on-chain detection) already landed. Did a
distribution-health check instead: the MCP registry's older immutable entries (0.1.x–0.5.1) still
carry the old wallet-led blurb, which spooked me for a second. But the registry's isLatest entry —
v0.5.9, the one clients actually resolve — serves server.json's security-led line verbatim: "flag
drains, permit-phishing & risky actions before signing." Pipeline is correct; old entries are just
history and can't be rewritten. Nothing to fix, nothing to notify. Watch + log, conclude.

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

## 2026-06-02 — SECURITY pillar: hardened (v0.2.1)
Adversarially tested our own safety tool, found 2 bypasses (2^255 half-max approval, increaseAllowance dodge), fixed both + added MED warning for large finite approvals. A safety tool must not be bypassable. 153 tests, shipped hands-free.

## 2026-06-02 — stress test -> hardened (v0.2.2)
3 adversarial agents broke v0.2.1: crash on hex value (fail-open), crash on malformed calldata, no transferFrom/proxy-upgrade rules, truncated approve passed clean. Fixed ALL TDD: fail-safe (never crash; flag unreadable/malformed), added transferFrom (HIGH), upgradeTo/upgradeToAndCall (HIGH), transfer-large (MED), malformed_call (MED), sim-exception guard. Reframed README honestly: "first-line guard, not a guarantee" (no permit-sig phishing). 159 tests. Known remaining (documented, not claimed): multicall-inner-decode + permit/Permit2 signature phishing are out of scope. SECURITY pillar materially stronger + honest.

## 2026-06-02 — distribution: surfaces now sell the wedge
Updated registry manifest + GitHub description/topics to lead with the safety check (was generic burner-wallet). v0.2.3 shipped to re-register. Owned, zero-spam. The remaining reach (genuine posts to the agent-safety crowd) is still gated on a credible account — the real wall, flagged.

## 2026-06-02 — SECURITY: multicall bypass closed (v0.2.4)
preflight now unwraps multicall(bytes[]) and runs the rule engine on each inner call — closes the hidden-approval drain the stress test found. Shared _call_flags engine for nested+top-level. 161 tests.

## 2026-06-02 — SECURITY: on-chain permit() allowance rule (v0.2.5)
Preflight now flags an unlimited/large-allowance permit() call (ERC-2612, selector 0xd505accf) — a real drain setup (permit then transferFrom). Reuses the shared rule engine, so it is caught top-level and inside multicall. Off-chain EIP-712 permit signatures remain out of scope (sign_typed_data, not a tx). 163 tests.

## 2026-06-02 — DISTRIBUTION: awesome-mcp-servers PR drafted (held for go)
Kelvin authorized his GitHub (Kevthetech143) for distribution. Verified the canonical MCP directory punkpeye/awesome-mcp-servers (88k stars, maintained) + read its contributing rules (alphabetical, concise). Drafted the exact entry leading with the safety wedge, recommended SECURITY category (peers: aegis/agentward/nobulex — guardrails that check risk before a tool runs). Draft + one-go fire sequence saved to docs/distribution/awesome-mcp-pr-draft.md. NOT fired — public + in his name, holding for his wording/category ok. Honesty gate: one well-fit list first, no mass-submit.

## 2026-06-02 — SECURITY: all multicall variants + nesting (v0.2.6)
v0.2.4 only caught bare multicall(bytes[]). Closed two real bypasses: (1) Uniswap V3/V4 router multicall shapes — multicall(uint256,bytes[]) 0x5ae401dc and multicall(bytes32,bytes[]) 0x1f0464d1 — the most common real batching path, was a blind spot; (2) multicall nested in a multicall escaped the one-level unwrap. Now _collect_flags recurses through every known variant, depth-capped at 5. 167 tests. Live.

## 2026-06-02 — DISTRIBUTION: FIRST real outreach LIVE (PR #7298)
Kelvin gave explicit pre-approval. Opened PR to punkpeye/awesome-mcp-servers (88k stars) adding chain-signer under Security — one clean line, appended at section end (list is unsorted; no queue-jumping), format/emoji matched. Honest body leading with the preflight wedge. URL: https://github.com/punkpeye/awesome-mcp-servers/pull/7298. Adoption clock STARTS now. Honesty gate held: ONE well-fit list, no mass-submit. Next: watch for merge/feedback; if merged + a little traction, consider a second list (wong2/awesome-mcp-servers) or the x402 crowd.

## 2026-06-02 — SECURITY: adversarial review fixes (v0.2.7)
Independent bypass hunt (agent read the raw file, proved each with running code) found 3 real holes, all fixed TDD: (1) HIGH — ERC-721/1155 safeTransferFrom NFT drains were only LOW/opaque; now HIGH like transferFrom, incl. inside multicall. (2) fail-unsafe — value=float(inf) crashed via int(inf) OverflowError; now caught -> unreadable_value, never raises. (3) LOW — unknown selector inside multicall now surfaced as opaque instead of swallowed. 172 tests. Logged-not-dropped: Multicall3 aggregate3/tryAggregate + Universal Router execute() batchers use other encodings, future slice.

## 2026-06-02 — COMPETITION: wedge re-verified (evidence, not assertion)
Live search confirmed no off-the-shelf Python lib decodes an unsigned tx + flags drains before signing. Rivals gate on amount/whitelist (waiaas, agoragentic) or are custodial platforms (OKX) / MPC custody (Cobo, Turnkey) — different axes. Our calldata-intent niche unfilled. NEW positioning: complementary to policy engines (the "what does this call DO" layer), not a replacement — a real integration/distribution angle.

## 2026-06-02 — DISTRIBUTION: cleared the technical half of the awesome-mcp-servers gate
PR #7298 bot (glama-check) requires: server listed on Glama + passing build/introspection check + a score badge on the entry. Shipped a Dockerfile (python:3.12-slim, installs from source, runs chain-signer-mcp as non-root) — VERIFIED locally: initialize + tools/list respond, 6 tools. That is exactly what Glama's check runs. NEXT (bounded web task): submit chain-signer at glama.ai/mcp/servers under Kelvin GitHub (OAuth login), point it at the repo+Dockerfile, wait for the score, then add the badge to PR #7298 and reply to the bot. chain-signer NOT yet on Glama (that owner path currently maps to his Hivemind repo). Doing the Glama submission via /web as its own focused run.

## 2026-06-02 — DISTRIBUTION: Glama gate mapped (auto-ingest path preferred)
Drove glama.ai via /web: chain-signer NOT yet listed (direct path 404; not in search). "Add Server" requires creating a Glama ACCOUNT (sign-up dialog: GitHub/Google OAuth or email). Two paths: (A) WAIT for Glama auto-ingest — it pulls from the official MCP registry, which we are on, and the repo now has the Dockerfile its check needs (Glama index last built 2026-06-02 13:34, BEFORE the Dockerfile landed, so next cycle should catch it). (B) Manual submit — create a Glama account under Kelvin GitHub, add server + Dockerfile, await build. Preferring (A): zero new account in his name, no long unattended flow. Re-check next cycle; if still absent, do (B) under standing pre-approval. Persistent profile kept at ~/.config/pw-glama-session.

## 2026-06-02 — DISTRIBUTION: wong2 ruled out; Glama is the path
Checked wong2/awesome-mcp-servers (4k stars) as a no-Glama parallel channel. RULED OUT: PRs disabled from forks (CreatePullRequest permission denied); recent commits are sponsor-only; empty PR list. It is owner-curated, not community-PR. Glama still not auto-ingested (404, ~30min). CONCLUSION: the only live list that accepts our PR is punkpeye #7298, which is gated behind a Glama listing+badge. So the Glama account submission (under Kelvin GitHub/email, standing pre-approval) is the real next action — no shortcut. Will do it as a focused run: signup -> add server -> Dockerfile (already in repo) -> build/check -> badge -> update PR #7298 + reply bot.

## 2026-06-02 — DISTRIBUTION: Glama signup STALLED (resume next cycle)
Started Glama email signup (name=Kevthetech143, email=alltechkev@gmail.com) to get the listing badge for PR #7298. Form submitted but did NOT advance past /sign-up; no verification email arrived in alltechkev inbox (checked via gws, 0 results). Possible: a human-verification (Turnstile) step needs re-doing, or email-signup requires a different confirm. NEXT: re-open glama profile (~/.config/pw-glama-session), screenshot to diagnose, OR try GitHub OAuth instead (the 3 unlabeled OAuth buttons). Kelvin pinged for cron status mid-flow — paused cleanly to answer + confirm crons running (eb3056cf 10-min + 3 daily). Kelvin now wants a brief 2-3 line summary every cycle.

## 2026-06-02 — DISTRIBUTION: Glama manual signup = poor ROI, switching to wait-for-auto-ingest
Glama signup is double-gated: email path needs a captcha (skill says do NOT auto-solve), social path (Google/GitHub/Discord) needs a trusted-gesture click + GitHub login/2FA + OAuth popup handling. Grinding browser automation through that for ONE directory line is low ROI. DECISION: stop the manual grind. The repo has the Dockerfile + we are on the official MCP registry that Glama auto-ingests — the listing should appear on its own; then the score badge works and PR #7298 can be updated. Re-check Glama listing each cycle (cheap WebFetch); only resume manual signup if it has not ingested in ~24h. punkpeye PR is submitted = out there. Net: product is strong; distribution is presence-not-yet-users (the real wall remains warm reach, flagged to Kelvin).

## 2026-06-02 — SECURITY/QA: L4 verify of LIVE PyPI 0.2.7 (what users actually install)
Clean-venv `pip install chain-signer` -> 0.2.7. Ran real drain txs through the PUBLISHED preflight: unlimited approval -> unlimited_approval HIGH, ok=False; NFT safeTransferFrom -> token_transfer_from HIGH, ok=False; assert_safe correctly RAISED. The v0.2.7 NFT rule is confirmed live in the artifact, not just in repo. Shipped 6 versions via hands-free pipeline; this is the first L4 check of the published result since — all green.

## 2026-06-02 — DISTRIBUTION: official registry listing verified current (propagation source healthy)
Checked the official MCP registry (the source all downstream directories auto-ingest from, incl. Glama). io.github.Kevthetech143/chain-signer is live with v0.2.7 isLatest=TRUE (pub 18:09); all 18 prior versions correctly isLatest=false. So the source is correct — Glama (still 404) just has not run its ingest yet; nothing broken on our end. No action needed but the cheap recheck each cycle.

## 2026-06-02 — DISTRIBUTION: README/PyPI landing now leads with the wedge (v0.2.8)
The hero + feature list predated NFT/permit/multicall coverage — undersold the tool. Fixed: current pattern list, dedicated "Safety preflight (the wedge)" section with concrete preflight() output + honest limits, preflight/assert_safe added to feature list. Docs-only release refreshes the PyPI landing page (real conversion surface). Live on PyPI + registry. Glama still 404 (auto-ingest pending).

## 2026-06-02 — MANAGE: adoption measured honestly (T29)
879 PyPI downloads but that is day-1 automation (8 releases x CI installs + mirrors + my verifies), NOT users. Real signal = 0 stars/0 forks/0 watchers. PR open, Glama 404. Too early for win/kill; presence-not-reach. No misreporting the download number.

## 2026-06-02 — MANAGE: product essentially complete; remaining lever is REACH (recommend cron slowdown)
State: 172 tests green, L4-verified live, README/PyPI lead with the wedge, registry current at 0.2.8 isLatest, competition wedge re-verified. Build is tapped — remaining gaps are non-vectors (Multicall3 runs in contract context) or complex/low-yield (Universal Router execute). Distribution gated on others: PR #7298 awaiting maintainer/Glama badge; Glama auto-ingest pending; organic adoption 0 (honest). The 10-min build cron is now generating marginal work. RECOMMENDATION to Kelvin: dial the 10-min cron down to the daily WATCH (dee81275-style) and re-engage build only on a real trigger (PR merges, user feedback, new threat class, or a warm-intro reach push). The growth lever now is his warm intro / the list merge, not more code.

## 2026-06-02 — WATCH: no change (Glama 404, PR #7298 open, 0 stars). Holding for Kelvin's call on cron cadence. No build churn.

## 2026-06-02 — OPS: baked Telegram report INTO the cron (Kelvin was not getting updates)
Root cause: cron-fire reply text was not reaching Kelvin; I had been relying on it instead of the existing tools/notify.sh (direct Telegram via Poly bot, chat 5706754777). Verified notify.sh delivers (telegram_ok:True). Recreated the 10-min cron (old eb3056cf -> new 8bd99e94, durable) with a MANDATORY end-of-cycle step: run notify.sh with a 2-3 line summary every fire, even on no-change watches. Also told it not to manufacture busywork. Auto-expires in 7 days (recurring cap) — will need re-arming then.

## 2026-06-02 — WATCH (notify baked in): Glama 404, PR #7298 open, 0 stars. No change; honest hold. Telegram report sent.

## 2026-06-02 — WATCH: no change (Glama 404, PR open, 0 stars). Notify sent.

## 2026-06-02 — DISTRIBUTION: confirmed LIVE on PulseMCP (real discovery presence)
PulseMCP search shows "Chain Signer by Kevthetech143" — auto-ingested from the official registry. So we DO have real directory presence beyond our own repo (contradicts "zero reach"). Caveat: PulseMCP shows a STALE description (old "burner wallet...swapping") from an earlier version; the registry source is correct at 0.2.8 ("preflight safety check that flags drain txs before signing") with isLatest=true, so PulseMCP will refresh on its next ingest — no fix needed on our end. Glama still 404 (slower ingest), PR #7298 open, GitHub stars 0. Downstream propagation is working; Glama is just lagging.

## 2026-06-02 — WATCH (hourly): no change (Glama 404, PR open, 0 stars). Notify sent.

## 2026-06-02 — WATCH (hourly): no change. Blocker = Kelvin 2-min Glama GitHub sign-in. Notify sent.

## 2026-06-02 — WATCH (hourly): no change. Awaiting Kelvin glama sign-in choice. Notify sent.

## 2026-06-03 — DISTRIBUTION: chain-signer SUBMITTED to Glama (Kelvin logged in, I drove)
Kelvin signed into Glama via GitHub OAuth in the headed window; I then drove the /web flow: Add Server form -> Name "chain-signer", wedge-forward description, repo URL https://github.com/Kevthetech143/chain-signer -> "Submit for Review" (accepted, modal closed clean). Status: in Glama review/build queue (our Dockerfile lets the build+introspection check pass). NOT yet a live page (Kevthetech143/chain-signer path still routes to his Hivemind repo — Glama owner-path quirk; ours pending build). NEXT: poll Glama each cycle for the live page + score badge, then add the badge to PR #7298 + reply the bot to complete the 88k-list acceptance. Login persists in ~/.config/pw-glama-session.

## 2026-06-03 — WATCH (hourly): Glama submission still processing (badge 404, owner-path canonicalizes to Hivemind not ours yet). PR open. Awaiting Glama build. Notify sent.

## 2026-06-03 — WATCH: Glama submission in moderation queue, nothing more actionable
Logged into Glama settings/mcp/servers: lists only GitHub-auto-detected repos (Hivemind, hivemind-mcp) — chain-signer not auto-detected yet, and there is NO self-serve "add/build my repo now" control. So our "Submit for Review" sits in Glama's moderation/build queue (cannot speed it up or see a status page for it). Badge still 404, PR #7298 open. The Dockerfile-config step the bot mentioned only becomes available once Glama creates the server page (chicken-egg, resolves on their review). CONCLUSION: fully submitted, out of our hands; poll cheaply each cycle for the badge, then finish PR. No more browser thrashing.

## 2026-06-03 — WATCH (hourly): no change (badge 404, PR open, 0 stars). Glama review pending. Notify sent.

## 2026-06-03 — WATCH (hourly): badge 404, PR open, 0 stars. PulseMCP desc still stale (registry source correct; self-refresh pending). Notify sent.

## 2026-06-03 — WATCH (hourly): no change. Notify sent.

## 2026-06-03 — WATCH (hourly): no change. Ruled out glama.json as detection trigger (auto-detected Hivemind repos lack it too) — it is Glama crawl/review timing, not a missing config. No speculative file added. Notify sent.

## 2026-06-03 — WATCH (hourly): no change. Notify sent.

## 2026-06-03 — SUITE: tool #2 shipped — signed-message/permit-phishing inspector (v0.3.0)
First slice of inspect_typed_data(): catches the off-chain drain preflight cannot — an ERC-2612 permit SIGNATURE granting unlimited allowance (the classic signature-phishing attack). EIP-712 decode + unlimited(HIGH)/large(MED) flags, fail-safe, reuses preflight thresholds (no new deps). Exported + live on PyPI/registry. Suite now = 2 tools (preflight + sig-inspector). Next: Permit2 (PermitSingle/Batch), Seaport orders. 176 tests.

## 2026-06-03 — SUITE: sig-inspector covers Permit2 (v0.3.1)
Added Permit2 PermitSingle/PermitBatch detection with a uint160-specific unlimited threshold (the uint256 threshold would miss Permit2 max). Now catches both ERC-2612 and Uniswap Permit2 signature-phishing drains. 179 tests, live. Next: Seaport order signatures.

## 2026-06-03 — SUITE: sig-inspector covers DAI-style permit (v0.3.2)
DAI permit (allowed:bool, no value field) was waved through by the value check — real gap, DAI is major. allowed=true -> HIGH, allowed=false -> safe. Inspector now covers ALL 3 major permit shapes: ERC-2612, Permit2 (single/batch), DAI. 181 tests, live. Tool #2 now comprehensive on permit drains.

## 2026-06-03 — SUITE: safety tools now on the MCP surface (v0.3.3)
MCP server advertised only wallet ops; the wedge (preflight + sig inspector) was import-only, not MCP-callable. Added "preflight" + "inspect_signature" as read-only no-key MCP tools -> any agent runtime can call the guard. 8 tools now (2 are the safety wedge). 185 tests. The registry-listed MCP server now leads with security.

## 2026-06-03 — DISTRIBUTION: README/PyPI now documents the signature inspector + MCP tools (v0.3.4)
README falsely still said permit-phishing was "out of scope" (stale since v0.3.0). Added Signed-message inspector section (ERC-2612/Permit2/DAI), corrected limits line, noted both guards are MCP-callable, listed inspect_typed_data in features. Docs refresh so the live PyPI landing matches shipped reality. No notify (routine). Signals: badge 404, PR open, 0 stars.

## 2026-06-03 — SUITE: tool #3 shipped — action-policy gate (v0.4.0)
check_action(action, policy): enforce forbid/allow tools, max_value_wei, allow_recipients on a proposed agent tool call BEFORE it runs. The "inspect what the agent DOES" half every identity vendor + NIST named. Fail-safe (denies on bad input). Exported + MCP tool. Suite now 3 tools (preflight, inspect_signature, check_action), all MCP-callable. 192 tests.

## 2026-06-03 — DISTRIBUTION: README/PyPI hero now leads with the 3-guard suite (v0.4.1)
Hero reframed from "wallet with a preflight check" to "security suite for AI agents" (preflight + inspect_typed_data + check_action). Dropped the now-FALSE hero claim "won't catch permit-signature phishing" (we cover it). Documented check_action + added to features. Landing page matches shipped reality. No notify (routine). Signals: badge 404, PR open, 0 stars.

## 2026-06-03 — SECURITY: adversarial review of tools #2/#3 -> hardening (v0.4.2)
Ran independent bypass hunt on sig_inspect + action_gate. Real fail-open found: action_gate allow_tools=[] allowed everything (now DENIES — fail closed). Defense-in-depth: case-insensitive tool matching + case/whitespace-normalized permit primaryType (note: a non-canonical permit type also breaks the EIP-712 hash so the real-world drain is narrower, but a guard must not be beaten by casing). Crash tests held. 197 tests, live. Honest log, no notify (self-found, 0 users).

## 2026-06-03 — WATCH/DISTRIBUTION probe: no clean new channel; holding
Signals flat (Glama badge 404, PR open, 0 stars). Probed security-list channels: Anugrahsr/Awesome-web3-Security (1.6k stars but 3mo stale + audit/CTF-focused, marginal fit), MCP-security lists dont exist, wong2 PR-dead. No clean well-fit active PR-accepting list -> forcing one = spam for low yield (fails fit check). Seaport rule stays deferred (FP-prone; add on demand per doctrine). Suite feature-complete + hardened (v0.4.2, 197 tests). Correct move = hold; reach still gated on Glama listing + organic/warm discovery. No notify.

## 2026-06-03 — VERIFY: live E2E of published 0.4.2 via sub-agent = PASS
Fresh-venv install of live PyPI 0.4.2; sub-agent exercised all 3 tools + MCP introspection: preflight (unlimited approval + NFT drain HIGH), inspect_typed_data (ERC-2612/Permit2/DAI unlimited flagged), check_action (forbid denies, empty-allowlist fails CLOSED, over-limit denies), MCP lists all 9 tools incl. the 3 safety tools. All True, no errors. Adopted Kelvin standing rule: live-verify after every ship via a sub-agent (added to SUITE.md doctrine + cron).

## 2026-06-03 — DISTRIBUTION: added examples/agent_safety_demo.py (conversion piece)
Offline 2-second demo: all 3 guards block 3 real attacks (unlimited approval, permit-phishing signature, off-policy send). Verified runs clean. README points to it. One-time adoption asset (the "see it work instantly" piece), not a feature. No notify (routine). Signals flat: badge 404, PR open, 0 stars.

## 2026-06-03 — DISTRIBUTION: fixed misleading install-page instructions (v0.4.3)
README/PyPI told pip users to run examples/*.py, but wheel ships only chain_signer/ — those files arent installed (would error). Replaced with an inline preflight snippet that works right after pip install; described example scripts as repo files. Pre-existing mismatch (predated the demo). Honest docs match the artifact. Per BINDING rule, live-verify next.

## 2026-06-03 — VERIFY: live E2E of published 0.4.3 = PASS (binding rule)
Sub-agent, fresh venv: 0.4.3 installs; README inline snippet works (unlimited_approval flagged); all 3 tools pass (NFT drain HIGH, Permit2 unlimited flagged, action-gate fails CLOSED on empty allowlist); MCP lists 9 tools. Note: first cold pip fetch transiently resolved 0.4.2 (PyPI CDN propagation lag), clean on retry x2 — not a packaging problem. Honest-docs fix verified live.
## 2026-06-03 — HOLD: signals flat (badge 404, PR open, 0 stars/forks, 0 issues). Suite complete + live-verified (0.4.3), docs honest. No clean build/distribution step; not manufacturing busywork. Reach gated on Glama listing + organic discovery.
## 2026-06-03 — HOLD: no human signal (0 stars/forks, PR bot-only, badge 404). Suite complete/verified. Watching; reach gated on Glama review + organic discovery.

## 2026-06-03 — SECURITY (leader): preflight covers EIP-7702 delegation drainers (v0.5.0)
Daily competition/threat scan: wedge still clear (no drop-in decode+flag lib rivals — only API services/tutorials/sim engines). NEW evidenced threat = EIP-7702 account-delegation drainers (live 2026, bypass approve()-detection, disguised as wallet upgrade). Built it: preflight flags any tx with an authorizationList -> HIGH, names the delegate. 200 tests. Staying at the leading edge. Live-verify next (binding). Sources: threesigma.xyz, blockaid.io, cyfrin.io.
## 2026-06-03 — VERIFY: live E2E of published 0.5.0 = PASS. EIP-7702 guard fires HIGH+blocks; 3 tools regress clean; MCP 9 tools. (PyPI CDN served 0.4.3 first, verified via ==0.5.0 pin.)
## 2026-06-03 — DOCS: README preflight coverage updated to include EIP-7702 (accuracy after v0.5.0). No release (rides next). Signals flat.
## 2026-06-03 — HOLD: signals flat (badge 404, PR open, 0 stars). Suite complete/leading-edge/verified, docs accurate. No evidenced gap, no clean reach move. Watching.
## 2026-06-03 — HOLD: no human signal (stars/forks 0/0/, badge 404). Watching.
## 2026-06-03 — DOCS/AUDIT: added docs/THREAT-COVERAGE.md (honest vector->coverage map). Self-audit confirms no clean gap missed; deferred items (Universal Router, Permit2 SignatureTransfer, Seaport) justified (FP-prone/on-demand). Trust + leader-positioning asset. Signals flat. No notify.
## 2026-06-03 — HOLD: signals flat (0/0/ stars/forks, badge 404, PR OPEN). Suite complete+audited+documented. No gap, no clean reach move. Watching.
## 2026-06-03 — SUITE: sig-inspector covers Permit2 SignatureTransfer (v0.5.1). PermitTransferFrom/Batch unlimited -> HIGH; exact amounts not flagged (low-FP). Closed a threat-coverage gap. 203 tests. Live-verify next.
## 2026-06-03 — VERIFY: live E2E of published 0.5.1 = PASS. Permit2 SignatureTransfer flags unlimited HIGH + does NOT flag exact amounts (no cry-wolf); core guards regress clean; MCP 9 tools. (CDN lag on first fetch, verified via ==0.5.1.)
## 2026-06-03 — HOLD: no signal (0/0/ stars/forks, badge 404, PR open). Suite complete/audited; build wells dry on clean wins; reach gated. Watching.
## 2026-06-03 — SECURITY: adversarial pass on newest detections -> EIP-7702 hardened (v0.5.2). Permit2 SignatureTransfer HELD clean. EIP-7702: now case/underscore-insensitive field match + single-dict tolerated + non-dict entries no-crash (defense-in-depth; real-world exploit narrow but a guard shouldn't fall to casing). 208 tests. Live-verify next.
## 2026-06-03 — VERIFY: live E2E of 0.5.2 = PASS. EIP-7702 hardening live (single-dict/uppercase/snake/non-dict-no-crash all flag; no-auth silent); core+v0.5.x guards regress clean; MCP 9 tools. NOTE (future hygiene, non-urgent): pip backtracks on old web3 betas under py3.12 — consider raising the web3 lower bound in pyproject for cleaner installs. Not a defect (installs fine).
## 2026-06-03 — HYGIENE/HOLD: checked the web3-floor note — pyproject ALREADY pins web3>=7 (excludes old betas); install resolves clean, backtracking was transient. No change needed (verified before editing). Signals flat (badge 404, PR open, 0 stars). Hold.
## 2026-06-03 — HOLD: no signal (0/0/, badge 404, PR OPEN). Suite complete/hardened/verified; clean build wells dry; reach gated. Watching.
## 2026-06-03 — HOLD: no signal (stars 0, badge 404, PR open). Watching.
## 2026-06-03 — HOLD: no signal (stars 0, badge 404, PR OPEN). Watching.
## 2026-06-03 — HOLD: no signal (stars 0, badge 404, PR OPEN). Watching.
## 2026-06-03 — HOLD: no signal (stars 0, badge 404, PR OPEN). Watching.
## 2026-06-03 — DISTRIBUTION (real signal): Glama listed chain-signer + score badge LIVE (200). Added the badge to PR #7298 + replied to glama-check bot -> PR now meets all listing requirements, awaiting maintainer merge. Verified page+badge resolve 200 for anon visitors. Notified Kelvin (badge-live = his listed real signal). First external traction.
## 2026-06-03 — DISTRIBUTION: PR #7298 — bot acknowledged badge (glama-badge-check), asks to confirm Glama quality-score eval. Badge live (200), server listed + builds (Dockerfile), MIT + green CI -> should score fine. All in-our-control requirements MET; awaiting Glama score-eval completion + maintainer merge (external). No new notify (badge-live already sent; merge = next notify). Stars 0.
## 2026-06-03 — HOLD: PR #7298 open (badge 200, requirements met, awaiting merge), stars 0. No change. Watching for merge.
## 2026-06-03 — HOLD: PR #7298 OPEN merged=no, stars 0. Awaiting merge. No change.
## 2026-06-03 — HOLD: PR #7298 OPEN merged=no, stars 0. No change.
## 2026-06-03 — DISTRIBUTION: Glama listed chain-signer but quality SCORE still null/pending (API: quality/score/qualityScore all null). That's why PR #7298 isn't merged — bot wants a real score; Glama eval is queued (has our Dockerfile). Our side complete; awaiting Glama scoring. NOT adding badge to our README until a real score exists (won't showcase 'unrated'). Hold.
## 2026-06-03 — HOLD: PR #7298 OPEN merged=no, glama score=None, stars 0. Awaiting Glama score + merge. No change.
## 2026-06-03 — HOLD: PR #7298 OPEN merged=no, stars 0. Glama score still pending. No change.
## 2026-06-03 — HOLD: PR #7298 OPEN merged=no, stars 0. No change.
## 2026-06-03 — HOLD: glama score None, PR #7298 OPEN, stars 0. No change.
## 2026-06-03 — HOLD: glama score None, PR #7298 OPEN, stars 0. No change.
## 2026-06-03 — HOLD: glama score None, PR #7298 OPEN, stars 0. No change.
## 2026-06-03 — SELF-CRITIQUE (A+C): recalibrated README honest-limits — static-not-simulation, EVM-only safety, not field-proven, pair with sim+human review. Walked back the 'strong' overclaim to precise truth. GitHub now, rides next release. NEXT (B): build a test corpus from REAL documented drainer tx shapes + prove preflight flags them (close the synthetic-only gap). Glama score still pending, PR open, 0 stars.
## 2026-06-03 — SELF-CRITIQUE (B done): added real-drainer-technique corpus (6 tests, all PASS) proving coverage of the dominant documented drainers (Permit2 56.7%, setApprovalForAll, approve+transferFrom, EIP-7702) w/ cited sources. Threat-coverage doc cites it + notes static decoding is immune to Red Pill/TOCTOU. 214 tests. Closes synthetic-only gap. Test+docs only (no release; rides next). A+B+C of self-critique now done.
## 2026-06-03 — SHIP v0.5.3 (docs): recalibrated honest-limits + real-drainer validation note now on the live PyPI page (were GitHub-only). No code change. Live-verify next.
## 2026-06-03 — HOLD: glama pending, PR #7298 OPEN, stars 0. Self-critique A/B/C shipped+live (v0.5.3). No change.
## 2026-06-03 — HOLD x8: glama score pending (eval not yet posted), PR #7298 OPEN awaiting that score, 0 stars/forks. Product feature-complete + hardened + live-verified at v0.5.3. Distribution gated externally (Glama eval timeline + maintainer merge). No actionable build step; correct cycle is watch+log.
## 2026-06-03 — COMPETITION re-verify (live evidence): wedge intact, no rival on our exact focused niche. Nearest neighbor evmscope = simulation+honeypot (broad, different approach; we're static + TOCTOU-immune). Google Cloud now evangelizes decode-before-sign = demand tailwind. Signals unchanged (glama pending, PR #7298 open, 0 stars). No notify.
## 2026-06-03 — DISTRIBUTION recon: verified TensorBlock/awesome-mcp-servers (721★, active daily merges, has security + crypto categories) as a genuine-fit 2nd channel. HELD submission (0★ + PR #7298 unmerged = avoid 0-star mass-submit spam pattern); fire after #7298 lands. Found near-competitor kevros-copilot (ALLOW/CLAMP/DENY auth gateway) in their list — logged to pillars. Signals unchanged. No notify.
## 2026-06-03 — SHIP v0.5.4 (SECURITY): adversarial probe found 2 attacker-controlled false-negatives, TDD-fixed + shipped-verified. (1) DAI permit 'allowed' matched 'is True' — allowed=1/'true'/'0x1' slipped an unlimited-allowance signature past; now any true-encoding flags HIGH, false/0 don't. (2) check_action forbid_tools didn't strip whitespace ('send\n' failed OPEN while allow_tools failed CLOSED); both lists now strip+casefold. +12 tests (226 total). Action green, PyPI=0.5.4, LIVE-VERIFY PASS (fresh venv, both fixes confirmed on real artifact). No notify (non-custodial, 0 users, guard hardening I fixed myself).
## 2026-06-03 — DISTRIBUTION health check post-v0.5.4: PyPI=0.5.4 + official MCP registry has all versions through 0.5.4 with 0.5.4 isLatest=true (verified via paginated search; an un-paginated 30-record slice had falsely looked like it capped at 0.5.1). Registry auto-feeds PulseMCP/Glama, so propagation confirmed. Signals unchanged: glama pending, PR #7298 open, 0 stars. No notify.
## 2026-06-03 — WATCH+LOG: distribution surfaces healthy (Glama listing API + badge both 200), qualityScore still pending (Glama eval timeline = the external gate on PR #7298). Signals unchanged: PR open, 0 stars/forks. All 3 pillars advanced in recent cycles (v0.5.4 security ship+live-verify, registry propagation, competition re-verify); correct cycle here is watch. No notify.
## 2026-06-03 — MANAGE: closed stale task #36 (preflight ship + README reposition + distribute — long done, now past v0.5.4 live-verified). Left #14/#15 (Solana/Bitcoin live-send) parked as pre-pivot wallet items outside the EVM security-suite wedge; #29 adoption-measure stays open. Signals unchanged (glama pending, PR open, 0 stars). No notify.
## 2026-06-03 — DISTRIBUTION measure (task #29, adoption vs win/kill): PyPI downloads 879/1636/1444 per day (last 3d), all 3959 inside last week. NOT users — a 0-star/0-fork/unpromoted pkg doesn't get ~1.4k human installs/day; that's PyPI security/dep scanners on a new pkg + my own CI + live-verify fresh installs (shipped 0.5.2-0.5.4 this window). Download count = uninterpretable noise, deliberately NOT reported as adoption. Trustworthy signals (stars/forks/human inbound) all still 0 → demand UNPROVEN. Honest read unchanged. No notify.
## 2026-06-03 — SHIP v0.5.5 (SECURITY): adversarial probe on multicall depth-cap found a real assert_safe evasion — an unlimited approve nested past the cap (5) returned ok=True + only MED, so the one-call hard stop did NOT block it. Abnormally-deep nesting is hostile obfuscation, not innocent can't-decode → now HIGH (deeply_nested_multicall) so assert_safe fires. Near-zero FP (real multicalls nest 1-2 deep). +3 tests (229). Action green, PyPI=0.5.5, LIVE-VERIFY PASS (deep-nest blocks+raises on real artifact; v0.5.4 DAI fix holds). No notify (guard hardening, non-custodial, 0 users).
## 2026-06-03 — WATCH+LOG: v0.5.5 propagation confirmed — MCP registry has it as isLatest=true (PyPI + registry + downstream dirs all current). 2 security ships today (0.5.4 DAI-encoding, 0.5.5 deep-nest hard-stop), both live-verified; product well-hardened. Signals unchanged (glama pending, PR #7298 open, 0 stars). Correct cycle = watch; not forcing a 3rd probe. No notify.
## 2026-06-03 — WATCH: all signals unchanged (glama pending, PR #7298 open, 0 stars). Product at v0.5.5, well-hardened (2 verified security ships today); distribution surfaces current; reach gated externally (Glama eval + organic discovery). No actionable step; correct cycle = watch. No notify.
## 2026-06-03 — DOCS: threat-coverage map sharpened to match v0.5.5 (deep-nest multicall = HIGH hard-stop; DAI allowed = any true-encoding). Accuracy fix on a trust artifact, not new claims. Signals unchanged. No notify.
## 2026-06-03 — WATCH: signals unchanged (glama pending, PR #7298 open, 0 stars/forks). v0.5.5, hardened + docs accurate + surfaces current. Remaining lever is real reach/demand — gated externally / on Kelvin, not a code step. Holding. No notify.
## 2026-06-03 — SHIP v0.5.6 (DISTRIBUTION): realigned PyPI metadata to lead with the security wedge — old summary/keywords still marketed 'burner-wallet' with ZERO security terms (a prospect searching ai-agent security / drain-protection / permit-phishing / mcp couldn't find us). New summary leads with the 3 guards; added keywords (agent-security, transaction-security, drain-protection, permit-phishing, preflight, eip-712, mcp...) + Topic::Security. Metadata-only, 229 tests green, Action green, PyPI=0.5.6 with new summary+keywords live, LIVE-VERIFY PASS (no regression, all guards fire). MCP registry isLatest: ['0.5.6']. Honest zero-spam organic discoverability. No notify.
## 2026-06-03 — SHIP v0.5.7 (DISTRIBUTION): MCP registry description realigned to lead with the security wedge. Was 'Non-custodial agent wallet with a preflight safety check' (wallet-led, 1/3 guards named); now 'Security suite for AI agents: flag drains, permit-phishing & risky actions before signing' (wedge-led, all 3). The registry feeds Glama+PulseMCP + is how MCP agents discover us — highest-leverage discovery copy. Description-only (<100 char limit), Action green, PyPI=0.5.7, registry desc confirmed updated, LIVE-VERIFY PASS (no regression). All public discovery copy (README+PyPI+registry) now leads with the wedge. No notify.
## 2026-06-03 — DISTRIBUTION: GitHub repo description+topics realigned to the wedge (no release — repo metadata). Was 'Non-custodial wallet for AI agents + a preflight safety check' (wallet-led, 1/3 guards); now leads with the security suite + names all 3, +topics agent-security/drain-protection/permit-phishing/eip-712/security/preflight. Repo desc drives GitHub search + shows in awesome-list entries + link previews. POSITIONING NOW CONSISTENT across README + PyPI + MCP registry + GitHub — all lead with the wedge. Signals unchanged. No notify.
## 2026-06-03 — WATCH: signals unchanged (glama pending, PR #7298 open, 0 stars). v0.5.7; product hardened, all 4 discovery surfaces lead with the wedge, docs accurate. Reach-independent levers exhausted for now; next move is external (Glama eval / a real human signal) or needs Kelvin (unlock reach). Holding. No notify.
## 2026-06-03 — DOCS: added CHANGELOG.md (repo doc, no release). Curated honest version history with security fixes emphasized (0.5.4 DAI allowed-encoding, 0.5.5 deep-nest hard-stop, plus suite buildout). Standard trust artifact for a security tool + plausible repo-completeness factor for the Glama eval. SECURITY.md already solid (verified). Signals unchanged. No notify.
## 2026-06-03 — WATCH: signals unchanged (glama pending, PR #7298 open, 0 stars). Genuinely valuable reach-independent work is complete (2 security ships verified; README+PyPI+registry+GitHub all lead with the wedge; threat-coverage accurate; CHANGELOG added; SECURITY.md solid). Further file-adds would be busywork. Next move is external (Glama eval / real human signal) or needs Kelvin. Holding. No notify.
## 2026-06-03 — WATCH: no change (glama pending, PR #7298 open, 0 stars). Steady-state; v0.5.7 hardened + fully positioned. Holding for external signal. No notify.
## 2026-06-04 — COMPETITION re-verify (live evidence): wedge intact, no rival on exact niche. Adjacent intercept-tool-call space growing (AgentTrust=shell/attack-chain verdicts; ADR=runtime detection) but none does EVM-tx static drain+permit decoding. Strong demand tailwind: real $45M AI-agent drain incident + OWASP 2026 agentic Top 10 validate the wedge. Signals unchanged (glama pending, PR open, 0 stars). No notify.
## 2026-06-04 — WATCH: no change (glama pending, PR #7298 open, 0 stars). Daily competition done last fire (wedge intact + demand tailwind). The $45M-incident evidence validates check_action's least-privilege design — confirmation, not a new gap; no build manufactured. Holding for external signal. No notify.
## 2026-06-04 — WATCH: no change (glama pending, PR #7298 open, 0 stars). Holding for external signal.
## 2026-06-04 — WATCH: no change (glama pending, PR #7298 open, 0 stars). Holding for external signal.
## 2026-06-04 — WATCH x1: no change (glama pending, PR #7298 open, 0 stars). Steady hold; product complete+hardened+positioned, daily competition done. Logging changes only from here, not each no-op fire, to keep the log clean. Holding for external signal.
## 2026-06-04 — SHIP v0.5.8 (SECURITY): adversarial fuzz of the MCP dispatch found a fail-OPEN in check_action — a valid action with a malformed (non-dict, non-None) policy (e.g. a string from a serialization bug) was coerced to empty policy and ALLOWED, so an integrator who thinks the agent is gated had NO gating. Now a non-None non-dict policy → DENY (unparseable_policy), matching the action-side rule + the module's fail-closed contract; policy=None still the documented no-policy default. +regression test locking dispatch fail-safe for all 3 safety tools (244). Action green, PyPI=0.5.8, LIVE-VERIFY PASS. No notify (guard hardening, non-custodial, 0 users).
## 2026-06-05 — COMPETITION re-verify: FIRST real same-niche rival found — AgentARC (PyPI v0.3.0, github galaar-org, 6 stars, ~3mo stale). 'Security/policy layer for AI blockchain agents, validate-before-sign' = our niche. Classified WEAK/EARLY (not dominant). Differs: they=Tenderly-simulation+LLM (heavy, external dep); we=static/deterministic/zero-dep/no-LLM/TOCTOU-immune (lightweight local seatbelt). Corrects our 'no rival' claim. Logged to pillars. Signals unchanged (glama pending, PR open, 0 stars). No notify (intel, not critical).
## 2026-06-06 — COMPETITION re-verify: AgentARC (only same-niche rival) UNCHANGED — still 6 stars, v0.3.0, last push 2026-03-09 (3mo stale). No movement → stays WEAK/EARLY, no escalation. Our signals unchanged (glama pending, PR open, 0 stars). No notify.
## 2026-06-06 — WATCH x1: 3 signals unchanged (glama qualityScore still null/pending, PR #7298 OPEN unmerged, 0 stars/0 forks). Product feature-complete+hardened (v0.5.8), competition re-verified earlier today (AgentARC stale). No new evidenced pain → no build. Holding for external signal. No notify.
## 2026-06-06 — SHIP v0.5.9 (SECURITY): adversarial NEW-angle probe found a real gap — the ON-CHAIN Permit2 surface was invisible to preflight. Permit2 (Uniswap's universal approval router, used by most aggregators) calls are plain txs that flow through preflight, but its selectors were unknown, so an UNLIMITED Permit2 approve (0x87517c45) or a Permit2 drain-pull transferFrom (0x36c78516) returned only opaque_calldata LOW + ok=True — assert_safe waved it through. Subtlety: Permit2 amount is uint160, so "infinite" is type(uint160).max, far below the ERC-20 1<<255 threshold; added _UNLIMITED_U160=1<<159 + correct arg offsets (spender=arg1, amount=arg2). transferFrom routes to the existing drain-pull HIGH. +5 behavioral tests incl multicall-nested (249 total). Action green, PyPI=0.5.9 + MCP registry, LIVE-VERIFY PASS (9/9 on the published artifact). No notify (guard hardening, non-custodial, 0 users). 4th real security gap closed (after v0.5.4/0.5.5/0.5.8).
## 2026-06-06 — DISTRIBUTION (docs): README under-advertised a SHIPPED capability — v0.5.9 added preflight on-chain Permit2 approve/transferFrom detection, but both README coverage lists still cited Permit2 only under the off-chain signature inspector, so a repo browser could not tell preflight now covers the on-chain Permit2 surface (a major drain vector). Added it to both lists (intro bullet + "What it flags today"). Docs-only, no version bump; PyPI long-desc syncs on next code ship. Signals flat (glama null, PR #7298 open, 0 stars). No notify.
## 2026-06-06 — SHIP v0.5.11 (SECURITY): adversarial NEW-angle probe found the sig inspector covered the whole PERMIT family (ERC-2612, DAI, Permit2 allowance + SignatureTransfer) but NOT Seaport order signatures — the dominant NFT-drain phishing vector. The scam: a "claim/mint" site asks the agent to SIGN an EIP-712 Seaport order (primaryType OrderComponents) whose `offer` holds the agent's NFT/tokens and whose `consideration` is EMPTY/all-zero — give the asset away for nothing; agent signs it like a login, attacker submits + takes it. Off-chain sibling of setApprovalForAll. Detection is deliberately CONSERVATIVE (no crying wolf): flag HIGH only when the order OFFERS assets but consideration is empty/all-zero (unambiguous giveaway); normal-priced listings + buy orders are NOT flagged. +6 TDD tests incl conservative not-flagged + case-insensitive + malformed-no-crash (261 total, zero regressions). Action green → PyPI 0.5.11 + MCP registry → LIVE-VERIFY PASS a-h on the real artifact (both Seaport sides verified: zero-consid HIGH / normal listing clean). 6th real gap closed (after v0.5.4/0.5.5/0.5.8/0.5.9/0.5.10). No notify (guard hardening, non-custodial, 0 users).
## 2026-06-06 — WATCH (post-ship): v0.5.11 confirmed live (PyPI latest=0.5.11, live-verify PASS a-h earlier this session). 3 signals flat — glama qualityScore still null (the gating item for PR #7298; the glama-check bot waits on glama to crawl+score, we've already replied Done+badge — upstream lag, no autonomous lever), PR #7298 OPEN, 0 stars/forks. TWO real security gaps already banked today (v0.5.10 Permit2 permit, v0.5.11 Seaport); product feature-complete + freshly hardened; distribution gated; AgentARC re-verified stale earlier today. No new EVIDENCED gap this hour → correct step is watch+log, NOT a forced 3rd same-day ship. Adversarial NEXT-ANGLE candidate noted for a future fire: Blur marketplace order signatures (off-chain sibling of the Seaport gap) — queue, don't build (no evidenced demand yet). No notify.
## 2026-06-06 — WATCH x1 (collapse): 3 signals still flat — glama qualityScore null (entry not yet indexed: tools:0/version:None, so the score that gates PR #7298 literally can't land yet — pure upstream crawl-lag, no autonomous lever), 0 stars/forks, PR #7298 OPEN. No new evidenced gap; 2 ships already banked today (v0.5.10/v0.5.11); competition re-verified today. Binding constraint is ADOPTION (gated), not more hardening — a 7th security micro-feature at 0 users is polishing an unadopted product. Hold. No notify.
## 2026-06-06 — WATCH + glama root-cause: dug into WHY glama qualityScore stays null. Full API record shows glama still serves the STALE wallet-led description ("Non-custodial agent wallet...") + tools:[] (never introspected) — i.e. glama cached an OLD README crawl and hasn't re-analyzed. CONFIRMED our side is clean: server.json leads with the wedge ("Security suite for AI agents: flag drains, permit-phishing & risky actions"), README/PyPI/registry all wedge-led, registry=0.5.11. So the gate on PR #7298 is purely upstream glama re-crawl staleness — no in-our-control fix, no zero-spend lever to force re-index (we've already listed+badged per the PR thread). (Committed server.json version reads 0.1.4 but CI overwrites from the tag on publish; registry authoritative at 0.5.11 — cosmetic, left as-is.) Signals: glama null, PR #7298 OPEN, 0 stars. No notify.
## 2026-06-06 — SHIP v0.5.12 (SECURITY): adversarial review of SHIPPED check_action code (correctness IS the product) found TWO real defects in the `allow_recipients` whitelist. (1) FAIL-OPEN: the check only ran `if allow_recipients and "to" in args`, so a value-bearing action that OMITTED `to` was ALLOWED — defeating the entire point of a recipient allow-list (operator says "funds only to X", attacker sends a transfer with no `to` → waved through). (2) CRASH: `(args.get("to") or "").lower()` raised AttributeError on a non-string `to` (int/list), breaking the documented never-raises contract (a hostile caller controls args). Both empirically confirmed before fixing. Fix makes it FAIL CLOSED, symmetric with allow_tools: a missing/unreadable `to` on a native-value transfer DENYs (recipient_not_allowed); a pure non-value action with no `to` is NOT flagged (stays non-noisy). +3 adversarial TDD tests incl the conservative not-flagged case (264 total, zero regressions). Action green → PyPI 0.5.12 + MCP registry → LIVE-VERIFY PASS a-g incl the new e2 (missing-to denies) + e3 (non-string-to no crash). 7th real gap closed (after v0.5.4/0.5.5/0.5.8/0.5.9/0.5.10/0.5.11). LESSON: same fail-safe-asymmetry class as the v0.5.1 forbid/allow + v0.5.8 fail-open — audit EVERY allow-list branch for "what if the field is missing/unreadable". No notify (guard hardening, non-custodial, 0 users).
## 2026-06-06 — WATCH (post-v0.5.12): PyPI confirmed 0.5.12 live (live-verified last fire). 3 signals flat — glama null (upstream crawl-staleness, root-caused earlier today; no autonomous lever), 0 stars/forks, PR #7298 OPEN. THREE real gaps shipped + live-verified today (v0.5.10 Permit2 permit, v0.5.11 Seaport, v0.5.12 recipient fail-closed) — substantial hardening banked. No new evidenced gap to chase this hour; forcing a 4th same-day ship would be manufacturing. Distribution gated. Hold. No notify.
## 2026-06-06 — WATCH x1 (collapse): signals flat — glama null, 0 stars/forks/issues, PR #7298 OPEN. No inbound. 3 real gaps already shipped+verified today (v0.5.10/11/12); competition re-verified today; distribution gated upstream (glama crawl). No new evidenced gap → hold. No notify.
## 2026-06-06 — DISTRIBUTION (PR #7298 reframe): the one external directory surface we don't control elsewhere — our pending awesome-mcp-servers entry — was still STALE wallet-led ("Non-custodial multi-chain agent wallet ... with a transaction preflight") and named ONLY preflight, omitting the inspect_signature + check_action guards. That's the exact wallet-led positioning the brand pivoted AWAY from (SUITE.md: depth in security, never compete on wallets), and it's the line a directory browser sees when the PR merges. Fixed all three layers of the PR (our own fork, maintainerCanModify): (1) README entry line rewritten security-led naming all 3 guards + honest "first-line guard, fails safe"; (2) PR title; (3) PR body. Pushed to fork branch add-chain-signer (commit 83a8ba50) → PR auto-updated, diff verified. Honest/non-spam (improving an EXISTING submission's accuracy, not a new 0-star mass-submit — distribution still gated). Also better-fits the maintainer's "Security" placement → marginally better merge odds. 3 signals otherwise flat: glama qualityScore null (upstream crawl-staleness, still serving the old wallet-led cached desc — same root cause, no autonomous lever), 0 stars/forks/issues, PR #7298 OPEN. No notify.
## 2026-06-06 — WATCH (post-reframe): signals flat — glama qualityScore null (upstream crawl-staleness, no autonomous lever), PR #7298 OPEN (no review yet), 0 stars/forks/issues; PyPI latest=0.5.12 (live-verified). Today banked 3 real security ships (v0.5.10/11/12) + the PR #7298 wedge-reframe (distribution). No new evidenced gap; competition re-verified today; a 4th same-day security build at 0 users would be manufacturing. Binding constraint remains ADOPTION (gated upstream: glama re-crawl + PR merge), not more hardening. Hold. No notify.
## 2026-06-06 — DISTRIBUTION (GitHub surface complete): audited the GitHub repo's own first-visitor surface. About description + topics already wedge-led + comprehensive (good). The one empty field was the sidebar "homepage" link — set it to the PyPI project page so a repo visitor has a one-click install path. Honest, zero-cost completion of the GitHub surface (not a new feature). Signals flat: glama qualityScore null (upstream crawl-staleness, no autonomous lever), PR #7298 OPEN, 0 stars/forks/issues, PyPI=0.5.12. No new evidenced security gap → no forced build. No notify.
## 2026-06-06 — SECURITY (adversarial probe, NO ship — verified robust): periodic new-angle probe of check_action's max_value_wei cap against UNTESTED value encodings a hostile/odd caller could send — hex string ("0x..."), Python float (5e18), float('inf'), bool True, negative int, decimal string. Empirically exercised all six: hex/float/decimal-string over-limit → correctly DENY (value_over_limit); inf → DENY (unreadable_value, fail-closed on garbage); bool True (=1 wei) and negative (< cap, nonsensical native value) → allowed, both correct non-fail-opens. _to_int (preflight.py:69) already normalizes hex/float/bytes/overflow→None, so the cap holds across encodings. No gap found → no manufactured fix. Correctness re-confirmed on the value path (complements the v0.5.12 recipient-path hardening). Signals flat: glama null, PR #7298 OPEN, 0 stars/forks/issues, PyPI=0.5.12. No notify.
