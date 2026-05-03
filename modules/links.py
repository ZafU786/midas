"""
ECサイトの検索URL生成 / Pollinations AIによる商品イメージ画像URL生成
"""
import urllib.parse


def get_search_urls(product_name: str) -> dict[str, str]:
    """商品名からECサイト各社の検索結果URLを生成する。
    ヤフオクは「即決のみ」フィルタ付き(fixed=2)を使用。
    """
    q = urllib.parse.quote(product_name)
    return {
        "楽天市場": f"https://search.rakuten.co.jp/search/mall/{q}/",
        "Yahoo!ショッピング": f"https://shopping.yahoo.co.jp/search?p={q}",
        "Amazon": f"https://www.amazon.co.jp/s?k={q}",
        "メルカリ": f"https://jp.mercari.com/search?keyword={q}&status=on_sale&sort=price&order=asc",
        "ヤフオク即決": f"https://auctions.yahoo.co.jp/search/search?p={q}&fixed=2&exflg=1",  # 即決のみ
        "ヤフオク": f"https://auctions.yahoo.co.jp/search/search?p={q}&fixed=2&exflg=1",  # 互換用も即決
        "ラクマ": f"https://fril.jp/s?query={q}",
        "ブックオフ": f"https://shopping.bookoff.co.jp/search/keyword/{q}",
        "PayPayフリマ": f"https://paypayfleamarket.yahoo.co.jp/search/{q}",
    }


def get_image_url(product_name: str, width: int = 400, height: int = 300) -> str:
    """
    Pollinations.ai（無料・APIキー不要）でAI商品イメージ画像URLを生成する。
    商品名を英訳的なプロンプトに変換せず、そのまま渡してOK（多言語対応）。
    """
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
    "ラクマ": "🟩",
    "ブックオフ": "📕",
    "PayPayフリマ": "💰",
}
