"""
利益計算エンジン
各プラットフォームの手数料を考慮して純利益・利益率を算出する
"""

# 各プラットフォームのデフォルト手数料率
PLATFORM_FEE_RATES = {
    "メルカリ": 0.10,
    "ラクマ": 0.06,
    "Amazon": 0.10,
    "ヤフオク": 0.10,
}

# 売れ行きスコア（判定に使用）
SPEED_SCORES = {
    "1日以内": 5,
    "3日以内": 4,
    "5日以内": 3,
    "1週間以上": 2,
    "売れてない": 1,
}


def calc_profit(
    sell_price: float,
    buy_price: float,
    platform: str = "メルカリ",
    shipping: float = 0,
    other_cost: float = 0,
    custom_fee_rate: float | None = None,
) -> dict:
    """
    純利益と利益率を計算する

    Args:
        sell_price: 販売価格（円）
        buy_price: 仕入れ価格（円）
        platform: 販売プラットフォーム
        shipping: 送料（円）
        other_cost: その他経費（円）
        custom_fee_rate: カスタム手数料率（0.0〜1.0）。Noneの場合はデフォルト値を使用

    Returns:
        {
            "fee_rate": 手数料率,
            "fee_amount": 手数料額,
            "net_profit": 純利益,
            "profit_rate": 利益率（%）,
            "verdict": 判定（"BUY!" / "検討" / "スキップ"）,
            "verdict_color": 表示色コード,
        }
    """
    fee_rate = custom_fee_rate if custom_fee_rate is not None else PLATFORM_FEE_RATES.get(platform, 0.10)
    fee_amount = sell_price * fee_rate
    net_profit = sell_price - buy_price - fee_amount - shipping - other_cost
    profit_rate = (net_profit / sell_price * 100) if sell_price > 0 else 0.0

    return {
        "fee_rate": fee_rate,
        "fee_amount": round(fee_amount),
        "net_profit": round(net_profit),
        "profit_rate": round(profit_rate, 1),
    }


def get_verdict(net_profit: float, speed_label: str, min_profit: float = 500) -> dict:
    """
    売れ行き・利益額から仕入れ判定を返す

    Args:
        net_profit: 純利益（円）
        speed_label: 売れ行きラベル（SPEED_SCORES のキー）
        min_profit: BUY!判定の最低利益額

    Returns:
        {"verdict": str, "emoji": str, "color": str}
    """
    speed_score = SPEED_SCORES.get(speed_label, 1)

    if net_profit >= min_profit and speed_score >= 3:
        return {"verdict": "買え!", "emoji": "🟢", "color": "green"}
    elif net_profit >= max(200, min_profit / 2) and net_profit < min_profit:
        return {"verdict": "検討", "emoji": "🟡", "color": "orange"}
    else:
        return {"verdict": "スキップ", "emoji": "🔴", "color": "red"}


def calc_all_platforms(
    sell_price: float,
    buy_price: float,
    shipping: float = 0,
    other_cost: float = 0,
) -> dict[str, dict]:
    """全プラットフォームの利益を一括計算する"""
    results = {}
    for platform in PLATFORM_FEE_RATES:
        results[platform] = calc_profit(sell_price, buy_price, platform, shipping, other_cost)
    return results


def get_speed_options() -> list[str]:
    """売れ行き選択肢のリストを返す"""
    return list(SPEED_SCORES.keys())
