"""
Yahoo!ショッピングAPI連携モジュール
Yahoo! Shopping Web Service V3 で商品を検索する
"""

import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

YAHOO_ENDPOINT = "https://shopping.yahooapis.jp/ShoppingWebService/V3/itemSearch"


def search_items(
    keyword: str,
    max_price: int,
    hits: int = 20,
) -> list[dict]:
    """
    Yahoo!ショッピングで商品を検索する

    Args:
        keyword: 検索キーワード
        max_price: 仕入れ予算上限（円）
        hits: 取得件数（最大100）

    Returns:
        商品情報の辞書リスト。エラー時は空リスト。
    """
    client_id = os.getenv("YAHOO_CLIENT_ID")
    if not client_id:
        raise ValueError("YAHOO_CLIENT_ID が設定されていません。.envを確認してください。")

    params = {
        "appid": client_id,
        "query": keyword,
        "price_to": max_price,
        "results": min(hits, 100),
        "sort": "-sold",  # 売れ筋順
    }

    try:
        response = requests.get(YAHOO_ENDPOINT, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        hits_data = data.get("hits", [])
        items = [_normalize_item(item) for item in hits_data]

        time.sleep(0.5)  # レート制限対策
        return items

    except requests.exceptions.Timeout:
        raise ConnectionError("Yahoo!APIへの接続がタイムアウトしました。")
    except requests.exceptions.HTTPError as e:
        raise ConnectionError(f"Yahoo!APIエラー: {e.response.status_code} {e.response.text}")
    except Exception as e:
        raise RuntimeError(f"Yahoo!API呼び出し中に予期しないエラーが発生しました: {e}")


def _normalize_item(item: dict) -> dict:
    """Yahoo!ショッピングAPIのレスポンスを統一フォーマットに変換する"""
    return {
        "商品名": item.get("name", "")[:100],
        "仕入れ価格": int(item.get("price", 0)),
        "仕入れ元": "Yahoo",
        "仕入れ元URL": item.get("url", ""),
        "カテゴリ": _get_category(item),
        "画像URL": item.get("image", {}).get("medium", ""),
        "ショップ名": item.get("seller", {}).get("name", ""),
        "レビュー数": int(item.get("review", {}).get("count", 0)),
    }


def _get_category(item: dict) -> str:
    """カテゴリ名を取得する"""
    categories = item.get("categories", {}).get("leaf", [])
    if categories:
        return categories[0].get("name", "")
    return ""
