#!/bin/sh

# 牛刀小试作业二，获取OKEX交易所前一天BTC交割、永续合约的5m的K线数据，时区使用交易所默认的UTC
python fetch_hist_candle.py \
  -e 'okex' \
  -s 'BTC-USDT-[^-]+$' 'BTC-USD-[^-]+$' \
  -i '5m' \
  -p 1 \
  -z 'UTC' \
  -o '../data' \
  --market 'future' \
  --match-symbols \
  --items-per-request 200 \
  --sleep 1
