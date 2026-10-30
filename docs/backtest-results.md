# BTC signal backtest

Run on [Coin Backtest](https://chartbacktest.com/) on 2026-10-30. The site reported Binance candle data through 2026-10-30 07:00 UTC and ran in-browser without an account or API key.

## Strategy proxy

- BTC/USDT, 1-hour candles, long only.
- SMA(8) crosses above SMA(24) to enter; opposite cross exits.
- $10,000 starting balance, 90% position size, 1x leverage.
- Site defaults: 0.06% fee and 0.02% slippage per side.

This approximates the dashboard's current 8/24 rolling-average signal. It does not backtest a trained ML model; the dashboard currently has no trained model or historical feature pipeline.

## Result

The site summary reported +125.65% total ROI, −79.69% maximum drawdown, 32.2% win rate, 1,723 trades, 1.03 profit factor, 0.46 Sharpe, and a 14-trade maximum losing streak.

Its period table reported +12.19% for 7 years, then negative results for each shorter window: 5y −43.94%, 3y −7.02%, 2y −36.21%, 1y −38.30%, 6m −4.48%, 3m −0.09%, and 1m −13.84%. The headline and period table do not reconcile, so treat the headline ROI as unverified. The period table shows weak and inconsistent performance, with steep drawdowns.

[Open the saved BTC/SMA configuration and results](https://chartbacktest.com/?s=eyJjb2luIjoiYnRjIiwidGYiOiIxaCIsImNvbmZpZyI6eyJkaXJlY3Rpb24iOiJsb25nIiwidHJpZ2dlcnMiOlt7ImtpbmQiOiJtYUNyb3NzIiwibWFUeXBlIjoic21hIiwiZmFzdCI6OCwic2xvdyI6MjQsIm1vZGUiOiJnb2xkZW5Dcm9zcyJ9XSwiZmlsdGVycyI6W10sImV4aXRzIjp7Im9wcG9zaXRlU2lnbmFsIjp0cnVlfSwiY2FwaXRhbCI6eyJpbml0aWFsIjoxMDAwMCwiZmVlUGN0UGVyU2lkZSI6MC4wNiwic2xpcHBhZ2VQY3RQZXJTaWRlIjowLjAyLCJsZXZlcmFnZSI6MSwiZW50cnlQY3QiOjkwfX19)

Backtest results are historical simulations. They do not predict future performance.
