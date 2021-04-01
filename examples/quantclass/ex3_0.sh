# 少年意气篇，使用币安现货数据对OKEX期货进行回测（非作业）
python run_back_testing.py \
  ../data/binance/spot/BTC-USDT_5m_20170817_20210327.parquet \
  -p strategy.boll_trend pnl.okex.future \
  -c bbands_period=200 bbands_std=2 bbands_ma=sma \
     pnl_cash=10000 pnl_face_value=0.01 min_trade_precision=0 pnl_commission=0.0005 \
     pnl_slippage_mode=ratio pnl_slippage=0.001 \
     pnl_leverage_rate=3 pnl_min_margin_ratio=0.01