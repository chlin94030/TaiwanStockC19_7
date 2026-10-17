# Alpha Radar V19.7 — Ten-perspective research release

**This is a complete application source package**, not a zip to upload as a single GitHub file. Extract its root files to the existing GitHub repository; replace matching program files, preserve private `data/`, `.streamlit/secrets.toml`, and `FINMIND_TOKEN` outside the source archive. Keep `app.py` as the Streamlit entrypoint.

## Use
1. Install: `pip install -r requirements.txt`, then `streamlit run app.py`.
2. Sidebar: select **V19.7 十面向研究＋過去區塊決策驗證**. Choose date, stock universe and optional data. Data downloads are cached and may be rate-limited by the provider.
3. In `選股與規劃`: inspect **research / passed past-internal-gate / legacy control** separately. A high score is not a probability or an order.
4. In `歷史驗證`: expand **十面向研究** to review factor coverage, historical 5/20/60-session net returns, paired ETF 0050 comparison, and missing inputs. A separate market-caution/cash result does not imply stock-picking skill.
5. For research reproducibility: `python run_v19.py --help`, `python v197_audit.py --help`.

## Key corrections and limits
- 12 rankable factor coordinates covering ten research lenses; market context and tradeability operate OUTSIDE the stock ranking. Only a selected subset receives nonzero weight. Date-based financial history without verified publication is NOT treated as point-in-time evidence.
- Historical sector labels in the original input are current classifications and cannot authorize adoption; this comparison remains shadow research.
- Price-source labels and data availability are separate; an unverified official live quote never becomes an executable purchase price.
- 100 development cutoffs have already been repeatedly inspected in earlier releases. This run is NOT a new blind test, and the research source universe omits many historical/delisted and large-cap names.
- If no sparse/fixed candidate convincingly beats the original plus 0050 with past-completed outcomes, the adopted model remains the original. This is correct and should not be removed merely to make rankings change.
- A download/programming test PASS is not a performance advantage. Read `V197_PROTOCOL.md` and the separate V19.7 research/QA reports before interpreting results.
