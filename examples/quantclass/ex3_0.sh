# 少年意气篇，使用币安现货数据对OKEX期货进行回测（非作业）
python run_back_testing.py \
  ../data/course/BTC-USDT_5m.parquet \
  -p data.resample_time_window strategy.boll_trend pnl.okex.future \
  -c resample_period=15T resample_drop_zero_volume=1 resample_drop_zero_volume=1\
     bbands_period=400 bbands_std=2 bbands_ma=sma \
     pnl_cash=1000000 pnl_face_value=0.01 pnl_min_trade_precision=0 pnl_commission=0.0005 \
     pnl_slippage_mode=ratio pnl_slippage=0.001 \
     pnl_leverage_rate=3 pnl_min_margin_ratio=0.01