# Alpha Radar V19.7 | Ten-perspective design protocol

## Research status and limits
- Version: V19.7; development research, **not** a statistically established optimum or a buy signal.
- Historic input: 2023-10-16 through 2026-10-15 Yahoo_daily supplier prices furnished by the user; 92 codes including ETF 0050, 91 non-ETF tickers.
- Historical universe is NOT fully dated/complete: surviving-stock selection and industry-classification lookahead remain unresolved.
- Signals are computed from daily candles through cutoff T. Entry: next common trading session open; exit: T+5/20/60 session close, with the original fees/tax/slippage/gap/no-fill rules. Price-basis incompatibilities are not compared.
- Research uses 100 fixed seeded historical cutoffs previously exposed to development. They are **not a fresh blind holdout** and windows overlap, especially 60 sessions.
- Do NOT present top historical scores as forecast probabilities, calibrated limit-up chances, or automatic trading approval.

## Ten analytical lenses
1. Market breadth and trend: market/ETF context, **only** for a separately labeled risk/abstention research policy, NOT a constant additive stock score.
2. Industry rotation: peer-only sector momentum, requires at least three other eligible peers. The snapshot industry classification is not original historic classification; this factor is SHADOW RESEARCH ONLY.
3. 52-week price position: close divided by the rolling 252-session high; minimum 180 observed bars, ending at T.
4. Trend quality: signed 40-session displacement / sum absolute daily movement; relative 60-session ETF return requires actual ETF evidence.
5. Compression and breakout: 10/50-day lagged volatility ratio and price versus PRIOR 20-session range high.
6. Institutional flow: 20 complete, published vendor-date-shifted daily foreign/trust flow observations; no fabricated zero observations.
7. Revenue growth: only vendor/source disclosures with a verifiable available-at time; a reporting-month marker is NOT release time.
8. Earnings, cash-flow quality, and valuation: separate inputs; a missing EPS, cash-flow, or PE is NOT given a neutral score. Strict financial publication timing governs inclusion.
9. Downside risk: realized negative-volatility and drawdown proxies; past safety does not guarantee future price protection.
10. Liquidity and implementation: 20-session average traded value plus independent next-day price-gap, quantity, tax, fee and slippage assumptions.

## Selection design
- `v197_ten_pillars.py`: raw causal indicators -> same-date cross-sectional 0-100 percentiles (not probabilities), with explicit coverage and evidence status.
- `v197_selection.py`: a small pre-registered library of single-factor and up-to-three-factor scores. Original Alpha remains a separate comparison, never mandatory in every new candidate.
- Selection at cutoff T uses only previously COMPLETED, non-overlapping historic holding blocks; no future outcomes. A separate past-issued-policy validation stage tests the selection procedure. Comparisons also require compatible prices against 0050.
- Historical sector proxies or assumed publication lag may appear on shadow leaderboards but cannot pass the adoption selector.
- Fixed shadow profiles and market-caution/cash research are exported as separate strategies. A cash decision is never credited as improved stock selection.
- If no challenger meets the gate, adopted ranking stays the original control. **This is a result, not an application error.**

## Running
```bash
pip install -r requirements.txt
streamlit run app.py
# Existing downloaded history is used when you choose cache-only validation in the UI.
python run_v19.py --factor-design ten_angle_v197 --cache-only --optional-data --dates 100 --as-of 2026-10-15 --data data/v19 --output data/v19/cli_v197
python v197_audit.py data/v19/cli_v197/v19_results.json --prices data/v19/cli_v197/input_prices.csv.gz --output data/v19/cli_v197/ten_review
```
The `--cache-only` command expects an actual local `data/v19/history_prices.csv.gz`; do not replace it with synthetic test values. Optional financial/chip inputs must have evidence of availability at each historical cutoff.

## Genuine future validation
Freeze the version/code hash, candidate profiles, trading rules, and dataset release-time ledger. Evaluate later time periods that were never inspected during model design, or paper-trade timestamped forward recommendations. Check not only average returns but paired 0050 and equal-pool excess, win fraction, losing tails, effective transaction fills, and by-regime / by-sector stability. More random draws from the same exposed date range do NOT solve overfitting.
