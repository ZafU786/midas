"""
楽天市場API連携モジュール
楽天Webサービス IchibaItem/Search を使って商品を検索する
"""

import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

RAKUTEN_ENDPOINT = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20220601"


def search_items(
    keyword: str,
    max_price: int,
    hits: int = 20,
) -> list[dict]:
    """
    楽天市場で商品を検索する

    Args:
        keyword: 検索キーワード
        max_price: 仕入れ予算上限（円）
        hits: 取得件数（最大30）

    Returns:
        商品情報の辞書リスト。エラー時は空リスト。
    """
    app_id = os.getenv("RAKUTEN_APP_ID")
    if not app_id:
        raise ValueError("RAKUTEN_APP_ID が設定されていません。.envを確認してください。")

    params = {
        "applicationId": app_id,
        "keyword": keyword,
        "maxPrice": max_price,
        "hits": min(hits, 30),  # APIの上限は30件
        "sort": "-reviewCount",  # レビュー数順（人気順の近似）
        "format": "json",
    }

    try:
        response = requests.get(RAKUTEN_ENDPOINT, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        items = []
        for item_data in data.get("Items", []):
            item = item_data.get("Item", {})
            items.append(_normalize_item(item))

        time.sleep(0.5)  # レート制限対策
        return items

    except requests.exceptions.Timeout:
        raise ConnectionError("楽天APIへの接続がタイムアウトしました。")
    except requests.exceptions.HTTPError as e:
        raise ConnectionError(f"楽天APIエラー: {e.response.status_code} {e.response.text}")
    except Exception as e:
        raise RuntimeError(f"楽天API呼び出し中に予期しないエラーが発生しました: {e}")


def _normalize_item(item: dict) -> dict:
    """楽天APIのレスポンスを統一フォーマットに変換する"""
    return {
        "商品名": item.get("itemName", "")[:100],  # 長すぎる場合は切り詰め
        "仕入れ価格": int(item.get("itemPrice", 0)),
        "仕入れ元": "楽天",
        "仕入れ元URL": item.get("itemUrl", ""),
        "カテゴリ": item.get("genreName", ""),
        "画像URL": _get_first_image(item),
        "ショップ名": item.get("shopName", ""),
        "レビュー数": int(item.get("reviewCount", 0)),
    }


def _get_first_image(item: dict) -> str:
    """商品画像URLを取得する（最初の1枚）"""
    medium_image_urls = item.get("mediumImageUrls", [])
    if medium_image_urls:
        return medium_image_urls[0].get("imageUrl", "")
    return ""
