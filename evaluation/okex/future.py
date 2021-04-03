from functools import partial
from evaluation.position import position_from_signal, disallow_transaction_daily_time
from evaluation.position import position_from_signal
from evaluation.okex.equity_curve import OKExEquityCurve


def build(params):
    """
    OKEx合约
    """

    # OKEx每日特定时刻进行无负债结算，当日需交割合约不参与当日的无负债结算, 结算时，将暂停交易，结算结束后恢复下单委托与撮合
    disallowed_transaction = partial(disallow_transaction_daily_time, dtd_hour=params['dtd_hour'],
                                     dtd_minute=params['dtd_minute'])

    # 计算收益曲线
    return position_from_signal, disallowed_transaction, OKExEquityCurve(**params).calculate
