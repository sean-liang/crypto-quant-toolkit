from functools import partial
from pnl.position import position_from_signal, disallow_transaction_daily_time
from pnl.base import position_from_signal
from pnl.future_pnl import FuturePnL


def build(params):
    """
    OKEX合约资金曲线计算
    """

    # OKEx每日16:00（UTC+8）进行无负债结算，当日需交割合约不参与当日的无负债结算, 结算时，将暂停交易，结算结束后恢复下单委托与撮合
    disallowed_transaction_on_16pm_cst = partial(disallow_transaction_daily_time, utc_hour=8, utc_minute=0)

    # 计算收益曲线
    p = params
    pnl = FuturePnL(cash=p['pnl_cash'], face_value=p['pnl_face_value'],
                    min_trade_precision=p['pnl_min_trade_precision'], leverage_rate=p['pnl_leverage_rate'],
                    slippage_mode=p['pnl_slippage_mode'], slippage=p['pnl_slippage'],
                    commission=p['pnl_commission'], min_margin_ratio=p['pnl_min_margin_ratio'])

    return position_from_signal, disallowed_transaction_on_16pm_cst, pnl.calculate
