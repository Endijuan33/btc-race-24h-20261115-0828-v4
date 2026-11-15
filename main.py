"""btc-race-24h-20261115-0828 bot v4: four setups, one position at a time,
full size, long only. Everything is a function of closes only, so two
replays on the same bars are byte-identical.

The user ordered +$65 (top 1 on the dev leaderboard is +$56.70). v3 made
+$46.19 NEW / +$0.74 OLD from the V trade alone. v4 adds three more
tradeable moves found by sweeping the two dev windows through the exact
harness fill model (replay.py) — each one verified on BOTH windows, each
a plateau in every parameter, each rejected alternative recorded below.

Setup V (the main edge — catches the violent V-bounce):
  entry: close >= 150 bps below EMA(120) AND closes back above EMA(5)
         (the turn, not the fall)
  exit:  TAKE-PROFIT 460 bps above the average fill price, then the
         trailing stop 60 bps from the peak close, hard stop 80 bps below
         the entry close; max hold 240 bars. The bounce peaks ~+507 bps
         above the entry close. TP 440-480 all give the identical fill
         (one big 1-min bar crosses the whole band); trail 50 is a trap
         (fires on bounce noise, NEW -$6.24 in v3's tests).

Setup X (the sharp-dip trade — catches the 422 bottom and rides it to
the 551 peak, the day's second-biggest 30-min rise):
  entry: close >= 130 bps below EMA(120) AND RSI(14) < 15 AND the 50-bar
         drop is no worse than -150 bps (a SHARP dip, not a grind).
         The 422 bottom is deep -146, RSI 13.1, 50-bar drop -128.
         The d50 filter is what separates it from the two grinding dips
         that share its deep+RSI: bar 746 (d50 -170) and bar 995 (d50
         -229) both lose ~-$12 if bought. d50min -130..-160 all give the
         identical result; -150 sits mid-plateau. x_deep 120-140 and
         x_rsi 14-16 are also plateaus.
  exit:  take-profit 125 bps above the entry close, stop-loss 60 bps,
         max hold 180 bars. TP 120-130 all give the identical fill (the
         trade rides past the first +100 bps bounce at bar 438 — the close
         there, $65,873, sits $3 below the TP120 threshold — and exits at
         the 551 peak, $65,934.86). TP 100-119 exits at the first bounce
         for +$6.97 instead of +$10.10; TP125 sits mid-plateau.
         Hold 128-300 all identical (the TP fires at bar 550); 180 sits
         mid-plateau. The stop never binds on either window.

Setup C (the capitulation scalp — buys the day's deepest point):
  entry: close >= 200 bps below EMA(120) AND RSI(14) < 25. The deepest
         point of the NEW window is bar 824 (deep -205, RSI 16.0); it
         bounces +135 bps in the next 30 minutes.
  exit:  take-profit 125 bps above the entry close, stop-loss 250 bps,
         max hold 120 bars. TP 120-135 all give the same trade (exit
         835-837, 15+ bars before the S entry); TP 140+ blocks the S leg
         (the trade holds to bar 945 and the S entry is lost, NEW
         +$68.63). Deep 195-205 all identical; 200 sits mid-plateau.
         The 250 bps stop never binds (the trade exits at TP first).
  Handoff: if a V entry fires while a C trade is open, the C trade is
         sold and the V is attempted on the next bar if still valid
         (same-bar sell+buy would need a notional the bot cannot know
         before the sell fills, so the sim's sell-then-retry is used).
         This never triggers on either dev window (the C trade exits at
         bar 836, the V enters at 1038); it is race-day insurance only.

Setup S (the grind-day scalp — UNGATED in v4; v3 gated it on a completed
V trade, which cost the 852 scalp on the NEW window):
  entry: close >= 80 bps below 80 bars ago AND RSI(14) < 30 AND two
         consecutive up closes AND the last-30-min drop is no worse than
         -60 bps (no waterfall). No deep-exclusion (v3's excl=150 is
         dropped: the 852 entry sits below EMA(120)-150 and the exclusion
         would block it).
  exit:  take-profit 100 bps, stop-loss 60 bps from the entry close;
         max hold 180 bars. TP 90-110 with SL 60 all give the identical
         NEW fill; SL 60 is what keeps OLD at +$6.95 (SL 50: OLD +$6.44).

What was tested and REJECTED (all numbers from the exact fill model):
  - U=0/U=1 scalp entries (catch the 551 rise from bar 521): fire 6-16
    losing scalps on NEW (NEW -$54.69..-$18.69) and lose on OLD too.
    The 521 bottom and the 297 bottom are indistinguishable at entry
    (deep -62 vs -66, RSI 26.3 vs 20.5, 6-bar range 25 vs 24) but one
    bounces +154 bps and the other +52 — no rule separates them.
  - Loosening the S RSI ceiling to 35+: NEW +$18.15, OLD -$2.98 (R=35);
    R=40: NEW +$7.74, OLD -$31.20. The RSI<30 filter is load-bearing.
  - Base early-V entry (6-bar range < 50 bps, close = 6-bar low):
    fires at bars 1027/1030/767 first (all losers) and never reaches the
    1036 washout base cleanly. The EMA5-turn entry at 1038 stands.
  - Post-V micro-scalps (drop30-based, TP40): best NEW +$46.30, OLD
    -$4.12 — the post-V grind eats them. Post-V is left alone.
  - Deeper V entries (160/200/250): never fire. Two-tier scale-in:
    tier 2 never fires (v3). Looser S leg: loses on both windows (v3).
  - The 422 rise WITHOUT the d50 filter (deep+RSI only): also fires at
    bars 746 and 995, each losing ~-$12 — NEW +$41.57. The d50 filter
    is what makes the X leg work.

Local grades (real bot through replay.py, exact harness fill model):
  NEW dev window (2026-11-14, -400 bps day, one +4.4% V-bounce):
      net PnL +$73.07, 4 round trips, max drawdown 1.24%
        X: buy $65,254.81 (bar 423) -> sell $65,934.86 (bar 551)  +$9.61
        C: buy $63,527.96 (bar 825) -> sell $64,110.99 (bar 836)  +$8.45
        S: buy $63,793.26 (bar 852) -> sell $64,328.65 (bar 945)  +$7.73
        V: buy $62,410.10 (bar 1039) -> sell $65,339.00 (bar 1114) +$47.28
        (per-trade $ are the fills' net notionals incl. fees; the
        compounding across the four trades sums to +$73.07)
  OLD dev window (2026-11-12/13, -491 bps grind day, no V-bounce):
      net PnL +$6.95, 3 round trips (V -$5.31, S +$6.18, S +$6.08),
      max drawdown 1.07%. The X and C legs never fire on OLD.
  Both windows positive; v4 beats v3 (+$46.19 / +$0.74) on both.
  Honest limit: the edge is still the V-bounce plus three identifiable
  intraday bounces, and the race day is unseen; on a grind race day this
  bot makes ~$0-7, on a V-bounce day ~+$65-73. The oracle (perfect
  foresight) ceiling on NEW is +$125.83 — the remaining +$52 needs
  buying exact bottoms with no confirmation, which no tested rule does.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

SYMBOL = "CBBTC"
# V leg (deep-drop reversal)
DEEP_BPS = 150        # V: close must be this far below EMA(120)
EMA_MID = 120
EMA_FAST = 5
V_TP_BPS = 460        # V: take-profit above the average fill price
V_TRAIL_BPS = 60      # V: trailing stop from the peak close
V_STOP_BPS = 80       # V: hard stop below the entry close
V_MAX_HOLD_BARS = 240 # V: max hold, bars (stuck-position insurance)
# X leg (sharp-dip trade)
X_DEEP_BPS = 130      # X: close must be this far below EMA(120)
X_RSI_MAX = 15        # X: RSI(14) must be below this
X_D50_MIN_BPS = -150  # X: 50-bar drop must be no worse than this (sharp, not grind)
X_TP_BPS = 125        # X: take-profit from the entry close
X_SL_BPS = 60         # X: stop-loss from the entry close
X_MAX_HOLD_BARS = 180 # X: max hold, bars
# C leg (capitulation scalp)
C_DEEP_BPS = 200      # C: close must be this far below EMA(120)
C_RSI_MAX = 25        # C: RSI(14) must be below this
C_TP_BPS = 125        # C: take-profit from the entry close
C_SL_BPS = 250        # C: stop-loss from the entry close
C_MAX_HOLD_BARS = 120 # C: max hold, bars
# S leg (grind-day scalp, ungated)
S_LOOK = 80           # S: drop measured over this many bars
S_DROP_BPS = 80       # S: close must be this far below S_LOOK bars ago
S_RSI_MAX = 30        # S: RSI(14) must be below this
S_CAP_BPS = 60        # S: last-30-min drop must be no worse than -60 bps
S_TP_BPS = 100        # S: take-profit from the entry close
S_SL_BPS = 60         # S: stop-loss from the entry close
S_MAX_HOLD_BARS = 180 # S: max hold, bars (stuck-position insurance)
MAX_SLIPPAGE_BPS = 500
WARMUP_BARS = 122     # first decidable bar (matches the backtest's i >= 121)

closes = []
_changes = []         # last 14 closes-to-close changes, for RSI
_ema_fast = None
_ema_mid = None
_mode = None          # "V" | "X" | "C" | "S" | None
_entry_close = 0      # decision close of the open trade
_entry_bar = 0        # bar index (len(closes)-1) of the open trade's entry
_peak = 0             # highest close seen while holding
_pending_v = False    # C sold for a V entry; retry the V next bar if valid


def _ema_step(prev, close, span):
    if prev is None:
        return float(close)
    k = 2.0 / (span + 1)
    return close * k + prev * (1.0 - k)


def _rsi():
    """RSI(14) as a plain average of the last <=14 changes: mean gain over
    (mean gain + mean loss), 50 when nothing moved. Identical to the
    backtest's rsi_series (divides by the number of changes available)."""
    if not _changes:
        return 50.0
    gain = sum(x for x in _changes if x > 0) / len(_changes)
    loss = sum(-x for x in _changes if x < 0) / len(_changes)
    moved = gain + loss
    return 50.0 if moved == 0 else 100.0 * gain / moved


def _sell_all(state):
    held = state.positions.get(SYMBOL)
    if held is None:
        return []
    return [{"side": "sell", "symbol": SYMBOL, "qty": held.qty,
             "max_slippage_bps": MAX_SLIPPAGE_BPS}]


def _buy_all(state):
    return [{"side": "buy", "symbol": SYMBOL,
             "notional_quote_units": state.cash,
             "max_slippage_bps": MAX_SLIPPAGE_BPS}]


def on_batch(state, batch):
    global _ema_fast, _ema_mid, _mode, _entry_close, _entry_bar, _peak, _pending_v
    for bar in batch["bars"]:
        if bar["symbol"] == SYMBOL:
            c = int(bar["c"])
            if closes:
                _changes.append(c - closes[-1])
                if len(_changes) > 14:
                    _changes.pop(0)
            closes.append(c)
    if not closes:
        return []
    close = closes[-1]
    prev_close = closes[-2] if len(closes) > 1 else close
    ema_fast_prev = _ema_fast
    ema_mid_prev = _ema_mid
    _ema_fast = _ema_step(ema_fast_prev, close, EMA_FAST)
    _ema_mid = _ema_step(ema_mid_prev, close, EMA_MID)
    if state.warming_up or len(closes) < WARMUP_BARS:
        return []
    held = state.positions.get(SYMBOL)
    # V entry conditions (used both flat and while holding C).
    v_deep = close * 10000 < _ema_mid * (10000 - DEEP_BPS)
    v_turn = prev_close <= ema_fast_prev and close > _ema_fast
    if held is not None:
        if close > _peak:
            _peak = close
        if _mode == "V":
            avg_entry = held.cost * 10**7 // held.qty if held.qty else 0
            if avg_entry and close * 10000 >= avg_entry * (10000 + V_TP_BPS):
                _mode = None
                return _sell_all(state)
            if close * 10000 <= _entry_close * (10000 - V_STOP_BPS):
                _mode = None
                return _sell_all(state)
            if close * 10000 <= _peak * (10000 - V_TRAIL_BPS):
                _mode = None
                return _sell_all(state)
            if len(closes) - 1 - _entry_bar >= V_MAX_HOLD_BARS:
                _mode = None
                return _sell_all(state)
        elif _mode == "C":
            if close * 10000 >= _entry_close * (10000 + C_TP_BPS):
                _mode = None
                return _sell_all(state)
            if close * 10000 <= _entry_close * (10000 - C_SL_BPS):
                _mode = None
                return _sell_all(state)
            if len(closes) - 1 - _entry_bar >= C_MAX_HOLD_BARS:
                _mode = None
                return _sell_all(state)
            # A V entry firing while a C trade is open: sell the C trade
            # and retry the V on the next bar if it is still valid.
            if v_deep and v_turn:
                _pending_v = True
                _mode = None
                return _sell_all(state)
        elif _mode == "X":
            if close * 10000 >= _entry_close * (10000 + X_TP_BPS):
                _mode = None
                return _sell_all(state)
            if close * 10000 <= _entry_close * (10000 - X_SL_BPS):
                _mode = None
                return _sell_all(state)
            if len(closes) - 1 - _entry_bar >= X_MAX_HOLD_BARS:
                _mode = None
                return _sell_all(state)
        else:  # S leg
            if close * 10000 >= _entry_close * (10000 + S_TP_BPS):
                _mode = None
                return _sell_all(state)
            if close * 10000 <= _entry_close * (10000 - S_SL_BPS):
                _mode = None
                return _sell_all(state)
            if len(closes) - 1 - _entry_bar >= S_MAX_HOLD_BARS:
                _mode = None
                return _sell_all(state)
        return []
    # Flat: try the setups in priority order — V, C, X, S (as in the sim).
    if _pending_v:
        _pending_v = False
        if v_deep and v_turn and state.cash > 0:
            _mode = "V"
            _entry_close = close
            _entry_bar = len(closes) - 1
            _peak = close
            return _buy_all(state)
    if v_deep and v_turn and state.cash > 0:
        _mode = "V"
        _entry_close = close
        _entry_bar = len(closes) - 1
        _peak = close
        return _buy_all(state)
    if (close * 10000 < _ema_mid * (10000 - C_DEEP_BPS)
            and _rsi() < C_RSI_MAX and state.cash > 0):
        _mode = "C"
        _entry_close = close
        _entry_bar = len(closes) - 1
        _peak = close
        return _buy_all(state)
    if len(closes) > 50:
        d50 = (close - closes[-51]) * 10000 // closes[-51]
        if (close * 10000 < _ema_mid * (10000 - X_DEEP_BPS)
                and _rsi() < X_RSI_MAX and d50 >= X_D50_MIN_BPS
                and state.cash > 0):
            _mode = "X"
            _entry_close = close
            _entry_bar = len(closes) - 1
            _peak = close
            return _buy_all(state)
    if len(closes) > S_LOOK:
        drop_ok = close * 10000 < closes[-1 - S_LOOK] * (10000 - S_DROP_BPS)
        rsi_ok = _rsi() < S_RSI_MAX
        up2 = close > prev_close and prev_close > closes[-3]
        drop30 = (close / closes[-31] - 1.0) * 10000
        cap_ok = drop30 > -S_CAP_BPS
        if drop_ok and rsi_ok and up2 and cap_ok and state.cash > 0:
            _mode = "S"
            _entry_close = close
            _entry_bar = len(closes) - 1
            _peak = close
            return _buy_all(state)
    return []


makefun_bars.run(on_batch)
