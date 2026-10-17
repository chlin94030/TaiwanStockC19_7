from pathlib import Path
import json,sys,hashlib
import pandas as pd,numpy as np
import argparse,zipfile
parser=argparse.ArgumentParser(description='Fixed-hypothesis indicator diagnostic; not an optimized strategy.')
parser.add_argument('--bundle',required=True)
parser.add_argument('--output',default='indicator_review')
args=parser.parse_args()
ROOT=Path(args.output);(ROOT/'input').mkdir(parents=True,exist_ok=True);(ROOT/'results').mkdir(exist_ok=True)
with zipfile.ZipFile(args.bundle) as archive:
    for name in ('v19_results.json','input_prices.csv.gz','input_evidence.csv.gz','comparison.csv'):
        if name not in archive.namelist():raise ValueError('Missing '+name)
        if archive.getinfo(name).file_size > 256 * 1024 * 1024:
            raise ValueError('Archive member exceeds 256 MiB: '+name)
        (ROOT/'input'/name).write_bytes(archive.read(name))
from v19_config import Settings
from v194_selection import Prepared
r=json.loads((ROOT/'input/v19_results.json').read_text());cfg=Settings(**r['settings'])
from v19_features import build_panel
from v19_backtest import add_outcomes
p=pd.read_csv(ROOT/'input/input_prices.csv.gz');e=pd.read_csv(ROOT/'input/input_evidence.csv.gz')
f=build_panel(p,e,cfg);f,_=add_outcomes(f,cfg)
cal=pd.DatetimeIndex(sorted(f.date.unique()));bm=f[f.ticker==cfg.benchmark].set_index('date').calc_close.reindex(cal).pct_change(fill_method=None)
pieces=[]
for t,g in f.groupby('ticker',sort=False):
 g=g.sort_values('date').copy();c=g.calc_close;ret=g.ret1;rv=g.share_volume
 g['near_252_high_raw']=c/g.calc_high.rolling(252,min_periods=252).max()
 # Common trading-session alignment; beta uses only completed preceding observations.
 cs=g.set_index('date').calc_close.reindex(cal);ri=cs.pct_change(fill_method=None)
 beta=(ri.rolling(60,min_periods=45).cov(bm)/bm.rolling(60,min_periods=45).var().replace(0,np.nan)).shift(1)
 residual=ri-beta*bm
 score=residual.shift(5).rolling(60,min_periods=50).sum()/(residual.shift(5).rolling(60,min_periods=50).std().replace(0,np.nan)*np.sqrt(60))
 g['residual_momentum_60_skip5_raw']=g.date.map(score)
 g['low_max_return_20_raw']=-ret.rolling(20,min_periods=20).max()
 den=rv.shift(1).rolling(20,min_periods=20).sum().replace(0,np.nan)
 for key in ['trust','foreign','dealer']:
  # No imputation of missing net flows and no count of unsigned-volume proxies as actual trades.
  s=g[key+'_net'];g[key+'_persistence_20_raw']=s.rolling(20,min_periods=20).sum()/den
 g['revenue_3_observations_raw']=np.nan;g['revenue_accel_3v3_raw']=np.nan
 q=e[(e.ticker==t)&e.revenue_yoy.notna()].copy()
 if len(q):
  q['record_date']=pd.to_datetime(q.date);q=q.sort_values('record_date').drop_duplicates('record_date')
  q['scenario_available']=q.record_date+pd.Timedelta(days=14)
  # Never advance an explicitly later supplied availability timestamp.
  if 'available_at' in q:
   observed=pd.to_datetime(q.available_at,errors='coerce',utc=True).dt.tz_convert(None)
   q['scenario_available']=pd.concat([q.scenario_available,observed],axis=1).max(axis=1)
  month=q.record_date.dt.year*12+q.record_date.dt.month
  contiguous=month.diff().eq(1)
  mean3=q.revenue_yoy.rolling(3,min_periods=3).mean().where(contiguous.rolling(2,min_periods=2).sum().eq(2))
  q['revenue_3_observations_raw']=mean3
  q['revenue_accel_3v3_raw']=(mean3-mean3.shift(3)).where(contiguous.rolling(5,min_periods=5).sum().eq(5))
  q=q[['scenario_available','revenue_3_observations_raw','revenue_accel_3v3_raw']].sort_values('scenario_available')
  j=pd.merge_asof(g[['date']].sort_values('date'),q,left_on='date',right_on='scenario_available',direction='backward',tolerance=pd.Timedelta(days=60))
  for k in ['revenue_3_observations_raw','revenue_accel_3v3_raw']:g[k]=j[k].to_numpy()
 pieces.append(g)
f=pd.concat(pieces).sort_values(['date','ticker']).reset_index(drop=True)
new=['near_252_high','residual_momentum_60_skip5','low_max_return_20','revenue_3_observations','revenue_accel_3v3','trust_persistence_20','foreign_persistence_20','dealer_persistence_20']
for k in new:
 a=f[k+'_raw'].replace([np.inf,-np.inf],np.nan).where(f.eligible)
 n=a.groupby(f.date).transform('count');f[k]=(a.groupby(f.date).rank(method='average',pct=True)*100).where(n>=cfg.min_universe)
variants={k:{k:1.} for k in new}
variants.update(high_plus_turnover_equal={'near_252_high':.5,'r196_dollar_turnover':.5},residual_plus_turnover_equal={'residual_momentum_60_skip5':.5,'r196_dollar_turnover':.5},revenue_plus_turnover_equal={'revenue_3_observations':.5,'r196_dollar_turnover':.5},revenue_plus_compression_equal={'revenue_3_observations':.5,'squeeze_release':.5})
# Explicit existing-factor controls, not new indicators.
variants.update(turnover_control={'r196_dollar_turnover':1.},breakout_control={'r196_breakout':1.},compression_control={'squeeze_release':1.},trust_control={'r196_trust':1.})
cutoffs=pd.to_datetime(r['cutoffs']);pairs=[(d,g) for d,g in f[f.eligible & f.date.isin(cutoffs)].groupby('date',sort=True)]
keys=list(dict.fromkeys(k for w in variants.values() for k in w));cases=[];trades=[]
for h in cfg.horizons:
 prep=Prepared(pairs,f,keys,h,cfg);prep.penalty[:]=0
 for name,w in variants.items():
  z=prep.evaluate(w);scope='ASSUMED_REVENUE_LAG_NOT_PIT' if any('revenue_' in k for k in w) else 'PRICE_OR_VENDOR_NEXT_DAY_FLOW'
  for i,(d,g) in enumerate(pairs):
   raw=g.reindex(columns=list(w)).to_numpy(float);weights=np.array(list(w.values()))
   score=raw@weights;score[~np.isfinite(raw).all(axis=1)]=np.nan
   pick=g.assign(_score=score).dropna(subset=['_score']).sort_values(['_score','ticker'],ascending=[False,True]).head(cfg.top_k)
   # Coefficients/rankings fixed before looking at outcome values.
   known=bool(len(pick)==cfg.top_k and pick[f'net_{h}'].notna().all())
   direct=float(pick[f'net_{h}'].mean()) if known else np.nan
   assert (np.isnan(direct) and np.isnan(z['net'][i])) or np.isclose(direct,z['net'][i],atol=1e-12)
   cases.append(dict(date=str(d.date()),horizon=h,variant=name,timing=scope,selected=len(pick),available_stocks=int(np.isfinite(score).sum()),net=z['net'][i],mae=z['mae'][i],fill=z['fill'][i],basis=z['basis'][i]))
   for _,p in pick.iterrows():trades.append(dict(date=str(d.date()),horizon=h,variant=name,ticker=p.ticker,score=p._score,net=p[f'net_{h}'],entry_date=p.entry_date,exit_date=p[f'exit_date_{h}'],state=p[f'outcome_state_{h}'],timing=scope))
a=pd.DataFrame(cases);original=pd.read_csv(ROOT/'input/comparison.csv');summary=[];yearly=[]
for (h,v),g in a.groupby(['horizon','variant']):
 for ref in ['adaptive','baseline','benchmark_0050','equal_weight_universe']:
  b=original[(original.horizon==h)&(original.strategy==ref)][['date','mean_net','price_basis']].rename(columns={'mean_net':'ref','price_basis':'ref_basis'})
  j=g.merge(b,on='date');good=j.net.notna()&j.ref.notna()&((j.basis==j.ref_basis)|j.basis.eq('CASH')|j.ref_basis.eq('CASH'))
  j=j[good];summary.append(dict(horizon=h,variant=v,reference=ref,pairs=len(j),mean_net=j.net.mean(),reference_mean=j.ref.mean(),delta=(j.net-j.ref).mean(),win_fraction=(j.net>j.ref).mean() if len(j) else np.nan,timing=g.timing.iloc[0]))
  for yr,s in j.groupby(j.date.str[:4]):yearly.append(dict(horizon=h,variant=v,reference=ref,year=yr,pairs=len(s),mean_net=s.net.mean(),reference_mean=s.ref.mean(),delta=(s.net-s.ref).mean()))
a.to_csv(ROOT/'results/indicator_cases.csv',index=False);pd.DataFrame(trades).to_csv(ROOT/'results/indicator_trades.csv',index=False)
s=pd.DataFrame(summary);s.to_csv(ROOT/'results/indicator_summary.csv',index=False);pd.DataFrame(yearly).to_csv(ROOT/'results/indicator_years.csv',index=False)
# No binary state is required for replay.
print(s[s.reference=='adaptive'].to_string(index=False));print('FINISHED',len(a),len(trades))

from v19_config import TECH,prior
from v19_features import score_rows
cases=a
fits={(i['cutoff'],i['horizon']):i for i in r['fits']}
parts=[]
for x in cases.itertuples():
 g=f[(f.date==pd.Timestamp(x.date))&f.eligible].copy()
 g=g[np.isfinite(g[list(variants[x.variant])].to_numpy(float)).all(axis=1)]
 meta=fits[(x.date,x.horizon)];weights=prior(x.horizon,TECH) if meta['adopted_is_legacy_control'] else meta['challenger_weights']
 sc,_=score_rows(g,weights,min_coverage=1-1e-9)
 q=g.assign(score=sc).dropna(subset=['score']).sort_values(['score','ticker'],ascending=[False,True]).head(cfg.top_k)
 good=len(q)==cfg.top_k and q[f'net_{x.horizon}'].notna().all()
 y=q[f'net_{x.horizon}'].mean() if good else np.nan
 bases=set(q[f'return_basis_{x.horizon}'])-{'CASH'};basis=next(iter(bases)) if len(bases)==1 else 'CASH' if not bases else 'UNKNOWN'
 parts.append(dict(date=x.date,horizon=x.horizon,variant=x.variant,candidate=x.net,control_same_input_cohort=y,basis_match=basis==x.basis or basis=='CASH' or x.basis=='CASH'))
a=pd.DataFrame(parts);a.to_csv(ROOT/'results/same_cohort_cases.csv',index=False)
summary=[]
for (h,v),g in a.groupby(['horizon','variant']):
 valid=g.candidate.notna()&g.control_same_input_cohort.notna()&g.basis_match
 q=g[valid]
 dates=sorted(pd.to_datetime(r['cutoffs']));calendar=sorted(f.date.unique());last=None;disjoint=[]
 for d in dates:
  end=pd.Timestamp(calendar[calendar.index(d)+h])
  if last is None or d>last:disjoint.append(str(d.date()));last=end
 qd=q[q.date.isin(disjoint)]
 summary.append(dict(horizon=h,variant=v,pairs=len(q),candidate=q.candidate.mean(),same_cohort_control=q.control_same_input_cohort.mean(),delta=(q.candidate-q.control_same_input_cohort).mean(),disjoint_pairs=len(qd),disjoint_delta=(qd.candidate-qd.control_same_input_cohort).mean()))
s=pd.DataFrame(summary);s.to_csv(ROOT/'results/same_cohort_summary.csv',index=False)
print(s[s.variant.isin(['near_252_high','high_plus_turnover_equal','trust_persistence_20','compression_control','residual_momentum_60_skip5'])].to_string(index=False))

# Three-way paired comparison, on the same observable dates and price basis.
bmref=original[original.strategy.eq('benchmark_0050')][['date','horizon','mean_net','price_basis']].rename(columns={'mean_net':'benchmark','price_basis':'benchmark_basis'})
joined=a.merge(cases[['date','horizon','variant','basis']],on=['date','horizon','variant']).merge(bmref,on=['date','horizon'])
valid=joined.basis_match & joined.candidate.notna() & joined.control_same_input_cohort.notna() & joined.benchmark.notna()
valid &= (joined.basis==joined.benchmark_basis)|joined.basis.eq('CASH')|joined.benchmark_basis.eq('CASH')
three=[]
for (v,h),g in joined[valid].groupby(['variant','horizon']):
    three.append(dict(variant=v,horizon=h,n=len(g),candidate=g.candidate.mean(),same_cohort=g.control_same_input_cohort.mean(),benchmark=g.benchmark.mean(),wins_vs_benchmark=int((g.candidate>g.benchmark).sum())))
pd.DataFrame(three).to_csv(ROOT/'results/three_way_paired.csv',index=False)
