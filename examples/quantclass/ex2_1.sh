#!/bin/sh

# 牛刀小试作业一，获取币安交易所BTC/USDT, ETH/USDT, EOS/USDT, LTC/USDT现货的5m, 15m的K线数据，时区使用交易所默认的UTC
python fetch_hist_candle.py \
  -e 'binance' \
  -s 'BTC/USDT' 'ETH/USDT' 'EOS/USDT' 'LTC/USDT' \
  -i '5m' '15m' \
  -b '2017-09-04' \
  -z 'UTC' \
  -o '../data' \
  --market 'spot' \
  --items-per-request 1000 \
  --sleep 1