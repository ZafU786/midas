"""
ECサイトの検索URL生成 / Pollinations AIによる商品イメージ画像URL生成
+ アフィリエイトタグ対応（運営者の収益化用）

Streamlit Cloud では .streamlit/secrets.toml に以下を設定:
  AMAZON_AFFILIATE_TAG = "youraccount-22"
  RAKUTEN_AFFILIATE_ID = "youraffiliateid"
  YAHOO_AFFILIATE_SID = "yourvcsid"
  YAHOO_AFFILIATE_PID = "yourpid"
  MOSHIMO_A_ID = "your_moshimo_a_id"  # もしもアフィリエイト経由の場合
"""
import os
import urllib.parse


def _get(key: str, default: str = "") -> str:
    """env/secretsから値を取得"""
    v = os.getenv(key, "").strip()
    return v if v else default


def _amazon_url(query_encoded: str) -> str:
    base = f"https://www.amazon.co.jp/s?k={query_encoded}"
    tag = _get("AMAZON_AFFILIATE_TAG")
    if tag:
        return f"{base}&tag={tag}"
    return base


def _rakuten_url(query_encoded: str) -> str:
    base = f"https://search.rakuten.co.jp/search/mall/{query_encoded}/"
    aff_id = _get("RAKUTEN_AFFILIATE_ID")
    if aff_id:
        # 楽天アフィリエイトのリンク形式
        encoded_url = urllib.parse.quote(base, safe="")
        return f"https://hb.afl.rakuten.co.jp/hgc/{aff_id}/?pc={encoded_url}&m={encoded_url}"
    return base


def _yahoo_shopping_url(query_encoded: str) -> str:
    base = f"https://shopping.yahoo.co.jp/search?p={query_encoded}"
    sid = _get("YAHOO_AFFILIATE_SID")
    pid = _get("YAHOO_AFFILIATE_PID")
    if sid and pid:
        encoded = urllib.parse.quote(base, safe="")
        return f"https://ck.jp.ap.valuecommerce.com/servlet/referral?sid={sid}&pid={pid}&vc_url={encoded}"
    return base


def get_search_urls(product_name: str) -> dict[str, str]:
    """商品名からECサイト各社の検索結果URLを生成する。
    アフィリエイトタグが設定されていれば自動で付与。
    ヤフオクは即決のみフィルタ付き。"""
    q = urllib.parse.quote(product_name)
    return {
        "楽天市場": _rakuten_url(q),
        "Yahoo!ショッピング": _yahoo_shopping_url(q),
        "Amazon": _amazon_url(q),
        "メルカリ": f"https://jp.mercari.com/search?keyword={q}&status=on_sale&sort=price&order=asc",
        "ヤフオク即決": f"https://auctions.yahoo.co.jp/search/search?p={q}&fixed=2&exflg=1",
        "ヤフオク": f"https://auctions.yahoo.co.jp/search/search?p={q}&fixed=2&exflg=1",
        "ラクマ": f"https://fril.jp/s?query={q}",
        "ブックオフ": f"https://shopping.bookoff.co.jp/search/keyword/{q}",
        "PayPayフリマ": f"https://paypayfleamarket.yahoo.co.jp/search/{q}",
    }


def get_image_url(product_name: str, width: int = 400, height: int = 300) -> str:
    """Pollinations.ai でAI商品イメージ画像URLを生成"""
    prompt = (
        f"professional product photography of {product_name}, "
        "high quality, studio lighting, white minimal background, "
        "luxury e-commerce style, detailed, 8k"
    )
    encoded = urllib.parse.quote(prompt)
    return (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width={width}&height={height}&nologo=true&enhance=true"
    )


PLATFORM_ICONS = {
    "楽天市場": "🟥",
    "Yahoo!ショッピング": "🟪",
    "Amazon": "🟧",
    "メルカリ": "🟦",
    "ヤフオク": "🟨",
    "ヤフオク即決": "🟨",
    "ラクマ": "🟩",
    "ブックオフ": "📕",
    "PayPayフリマ": "💰",
}
