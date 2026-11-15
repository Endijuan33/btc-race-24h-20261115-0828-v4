# btc-race-24h-20261115-0828 v4

[![make.fun · btc-race-24h-20261115-0828](https://make.fun/badge/btc-race-24h-20261115-0828.svg)](https://make.fun/bounty/btc-race-24h-20261115-0828?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261115-0828)
[![rank](https://make.fun/badge/btc-race-24h-20261115-0828/Endijuan33/btc-race-24h-20261115-0828-v4/rank.svg)](https://make.fun/bounty/btc-race-24h-20261115-0828/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261115-0828)
[![reward](https://make.fun/badge/btc-race-24h-20261115-0828/Endijuan33/btc-race-24h-20261115-0828-v4/reward.svg)](https://make.fun/bounty/btc-race-24h-20261115-0828?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261115-0828)

A bot for the [make.fun bounty](https://make.fun/bounty/btc-race-24h-20261115-0828): race a BTC trading bot live for 24 hours on cbBTC 1-minute bars, $1,000 paper money. v4 of the submitted "Fair Filament" entry — same V-bounce edge, plus three more tradeable moves found by sweeping both dev windows through the exact harness fill model: a sharp-dip trade (X), a capitulation scalp (C), and an ungated grind-day scalp (S). Dev NEW **+$73.07** (target was +$65; dev top 1 is +$56.70), OLD **+$6.95**.

Pure Python, **stdlib only** — the kit's SDK shim is vendored under `vendor/`. Run as `python3 -P -s main.py` (the harness speaks `agent-fun/bars-replay/v1` over stdio).

## Strategy

Four setups, one position at a time, full size, long only:

- **V — deep-drop reversal.** Entry when the close is ≥150 bps below EMA(120) and closes back above EMA(5). Exit at a 460 bps take-profit above the average fill price, or a 60 bps trailing stop from the peak close, or an 80 bps hard stop. The bounce peaks ~+507 bps, so the TP captures +460 bps where the trail alone left +404 bps. TP 440–480 all give the identical fill — a plateau, not a spike.
- **X — sharp-dip trade.** Entry when the close is ≥130 bps below EMA(120), RSI(14) < 15, and the 50-bar drop is no worse than −150 bps (a sharp dip, not a grind). Catches the 422 bottom (deep −146, RSI 13.1, 50-bar drop −128) and rides it to the 551 peak. The 50-bar filter is what makes it work: the two grinding dips that share its deep+RSI (bars 746 and 995) each lose ~−$12 if bought. Exit at +125 bps take-profit or −60 bps stop.
- **C — capitulation scalp.** Entry when the close is ≥200 bps below EMA(120) and RSI(14) < 25 — the day's deepest point (bar 824, deep −205, RSI 16.0). Exit at +125 bps take-profit or −250 bps stop. Exits 15+ bars before the S entry, so it never blocks the scalp.
- **S — grind-day scalp (ungated in v4).** Entry when the close is ≥80 bps below 80 bars ago, RSI(14) < 30, two consecutive up closes, and the last-30-min drop is no worse than −60 bps. Exit at +100 bps take-profit or −60 bps stop. v3 gated this on a completed V trade, which cost the 852 scalp on the NEW window.

## Local grades (real bot through replay.py, exact harness fill model)

| Window | Day shape | Net PnL | Trades | Max DD |
|---|---|---|---|---|
| NEW dev (2026-11-14) | −400 bps, one +4.4% V-bounce | **+$73.07** | 8 | 1.24% |
| OLD dev (2026-11-12/13) | −491 bps grind, no bounce | **+$6.95** | 6 | 1.07% |

Both windows positive (v3 was +$46.19 / +$0.74). Deterministic: two replays byte-identical. Every parameter sits mid-plateau (X: deep 120–140, RSI 14–16, 50-bar filter −130..−160, TP 120–130, hold 128–300; C: deep 195–205, TP 120–135; V: TP 440–480, trail 60; S: TP 90–110, SL 60). Rejected with numbers: U=0/U=1 scalp entries, RSI ceiling ≥35, base early-V entry, post-V micro-scalps, deeper V entries, two-tier scale-in, looser S leg — see main.py for the full list.
