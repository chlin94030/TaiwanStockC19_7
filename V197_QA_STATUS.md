# V19.7 QA and acceptance

STATUS: Research computation completed on user-provided supplier data, with market-performance advantage not proven.

- The input has 63,843 daily candles over 92 symbols including 0050, plus 109,941 optional evidence observations. Strict publication handling intentionally excludes unverified monthly revenue and incomplete financial-statement ledgers.
- 100 exposed historical cutoffs x 5/20/60 sessions = 300 cases. Those windows overlap and are NOT an independent holdout.
- The original Alpha remains a separate comparison; fixed ten-angle shadow profiles, adaptive gate results, ETF, pool equal-weight and market-caution cash policy are separately exported.
- Ten-angle factor coverage includes price position, trend, compression, institutional flow, sector proxy, tail risk and liquidity; profitability/valuation histories are unavailable in this replay and are not invented.
- End-to-end actual Streamlit Cloud/mobile browser and exchange live quote endpoints were NOT tested in the user's deployed environment.
- 52-week high and realized-downside screens on 5 sessions show an exploratory, small favorable same-period mean excess, but none of the 20/60-session research profiles consistently beat 0050.
- No fresh uninspected historic period, full delisted-stock universe, historic industry-membership ledger, official limit-up labels or real market fills were established.
- The price supplier data were not independently re-queried and verified against exchange bars for each security.
- - **357 unique engineering tests passed** on the final research source, including 11 new ten-perspective tests; the versioned pre-existing assertion/fixture updates were limited to changed default-version expectations. Synthetic missing-field fallback was checked separately.
- Python modules compiled and the market replay completed. A later final byte-consistency replay is also run before distribution to detect a source/results mismatch.
- Historical status is **RESEARCH_PARTIAL**, which indicates some selected outcomes or benchmark prices are missing, not a failed program execution.
- On these 100 previously exposed development dates, the adopted policy still equals the legacy baseline; 5-session high-52 fixed research has +0.23% paired mean versus +0.03% for 0050 on 97 date/basis-matched cases. 20 and 60 session profiles have not established a robust excess over 0050.
- This is engineering/research acceptance, not a verified improved trading model or live account integration. Archive CRC and manifest verification are performed at packaging.
