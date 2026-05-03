"""
メルカリ検索URL生成・売価入力補助モジュール
スクレイピングは一切行わず、検索URLの生成のみを行う（規約遵守）
"""

from urllib.parse import quote_plus


MERCARI_SEARCH_BASE = "https://jp.mercari.com/search"

# 売れ行きラベルと表示用絵文字のマッピング
SPEED_LABELS = {
    "1日以内": "⚡ 1日以内に売れた",
    "3日以内": "🔥 3日以内に売れた",
    "5日以内": "✅ 5日以内に売れた",
    "1週間以上": "⚠️ 1週間以上前",
    "売れてない": "❌ 売れてない",
}


def build_search_url(keyword: str, sold_only: bool = True) -> str:
    """
    メルカリの検索URLを生成する（売り切れ商品のみ表示で相場確認）

    Args:
        keyword: 検索キーワード
        sold_only: Trueなら売り切れ商品のみ（相場確認に適している）

    Returns:
        メルカリ検索URL
    """
    encoded = quote_plus(keyword)
    status = "sold_out" if sold_only else ""
    url = f"{MERCARI_SEARCH_BASE}?keyword={encoded}"
    if status:
        url += f"&status={status}"
    return url


def build_active_search_url(keyword: str) -> str:
    """出品中の商品を検索するURLを生成する（現在の競合確認用）"""
    encoded = quote_plus(keyword)
    return f"{MERCARI_SEARCH_BASE}?keyword={encoded}&status=on_sale"


def get_speed_options() -> list[str]:
    """売れ行き選択肢（表示用ラベル）のリストを返す"""
    return list(SPEED_LABELS.values())


def get_speed_key(display_label: str) -> str:
    """
    表示用ラベルから内部キーに変換する

    Args:
        display_label: 絵文字付きの表示ラベル（例："⚡ 1日以内に売れた"）

    Returns:
        内部キー（例："1日以内"）
    """
    for key, label in SPEED_LABELS.items():
        if label == display_label:
            return key
    return "売れてない"
