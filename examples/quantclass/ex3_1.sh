# 少年意气篇，优化策略参数（使用遗传算法）
python optimize_parameters.py \
  ../data/course/BTC-USDT_15m.parquet \
  -m 'DE' -s 50 -i 2  \
  -b '2017-01-01' \
  -p data.copy_dataframe strategy.boll_trend evaluation.okex.future \
  -c bbands_period='[10, 1000, 10]' bbands_std='[0.2, 6, 0.2]' bbands_ma='ma' \
     dtd_hour=16 dtd_minute=0 \
     data_skip_days=10 \
     eval_cash=100000 eval_face_value=0.01 eval_min_trade_precision=0 eval_commission=0.0005 \
     eval_slippage_mode=ratio eval_slippage=0.001 \
     eval_leverage_rate='[1, 3, 1]' eval_min_margin_ratio=0.01