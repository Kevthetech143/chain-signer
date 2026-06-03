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
