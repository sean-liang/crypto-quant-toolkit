# 少年意气篇，使用币安现货数据对OKEX期货进行回测（非作业）
python optimize_parameters.py \
  ../data/course/BTC-USDT_5m.parquet \
  -b '2017-01-01' \
  -p data.resample_time_window strategy.boll_trend evaluation.okex.future evaluation.report\
  -c resample_period=15T resample_drop_zero_volume=1 resample_drop_zero_volume=1 \
     bbands_period=400 bbands_std=2 bbands_ma=sma \
     dtd_hour=16 dtd_minute=0 \
     eval_cash=1000000 eval_face_value=0.01 eval_min_trade_precision=0 eval_commission=0.0005 \
     eval_slippage_mode=ratio eval_slippage=0.001 \
     eval_leverage_rate=3 eval_min_margin_ratio=0.01