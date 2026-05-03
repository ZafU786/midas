"""
Amazon PA-API連携モジュール（後付け用スタブ）

PA-APIは審査が必要なため、当面は未実装。
将来的にここを埋めれば、rakuten_api / yahoo_api と同じインターフェースで使える。
"""


def search_items(keyword: str, max_price: int, hits: int = 20) -> list[dict]:
    """
    Amazon PA-APIで商品を検索する（未実装）

    実装する場合の参考:
    - SDK: python-amazon-paapi
    - 認証情報: ACCESS_KEY, SECRET_KEY, ASSOCIATE_TAG
    - 返り値は rakuten_api._normalize_item と同じ形式に揃える
    """
    raise NotImplementedError("Amazon PA-APIは未実装です。承認取得後に実装してください。")
