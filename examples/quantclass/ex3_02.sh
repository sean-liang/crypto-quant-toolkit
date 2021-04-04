# 少年意气篇，使用币安现货数据对OKEX期货进行回测（非作业），使用预先合成的15分钟数据
python run_back_testing.py \
  ../data/course/BTC-USDT_5m_RESAMPLE_15T.h5 \
  -b '2021-01-01' \
  -p strategy.boll_trend evaluation.okex.future evaluation.report\
  -c bbands_period=400 bbands_std=2 bbands_ma=sma \
     data_skip_days=10 \
     dtd_hour=16 dtd_minute=0 \
     eval_cash=100000 eval_face_value=0.01 eval_min_trade_precision=0 eval_commission=0.0005 \
     eval_slippage_mode=ratio eval_slippage=0.001 \
     eval_leverage_rate=3 eval_min_margin_ratio=0.01