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


# ===== 広告バナーHTML生成 =====
# 楽天のおすすめカテゴリ（ランキングトップへの誘導）
RAKUTEN_HOT_CATEGORIES = [
    {"name": "デイリーランキング", "url": "https://ranking.rakuten.co.jp/daily/", "icon": "👑", "label": "今日売れてる商品"},
    {"name": "セール会場", "url": "https://event.rakuten.co.jp/campaign/", "icon": "🔥", "label": "お得なセール"},
    {"name": "スーパーセール", "url": "https://event.rakuten.co.jp/campaign/super-deal/", "icon": "💎", "label": "最大80%OFF"},
    {"name": "新着商品", "url": "https://search.rakuten.co.jp/search/mall/?s=2", "icon": "✨", "label": "新着アイテム"},
]


def _wrap_rakuten_affiliate(target_url: str) -> str:
    """任意の楽天URLをアフィリエイトリンクに変換"""
    aff_id = _get("RAKUTEN_AFFILIATE_ID")
    if not aff_id:
        return target_url
    encoded = urllib.parse.quote(target_url, safe="")
    return f"https://hb.afl.rakuten.co.jp/hgc/{aff_id}/?pc={encoded}&m={encoded}"


def get_top_banner_html() -> str:
    """トップバナー：楽天セール導線（アフィリエイト付き）"""
    aff_id = _get("RAKUTEN_AFFILIATE_ID")
    if not aff_id:
        return (
            '<div class="ad-slot ad-banner">'
            '📢 PR枠 — アフィリエイトIDが未設定です（Streamlit Cloud Secretsで設定）'
            '</div>'
        )

    cards = ""
    for cat in RAKUTEN_HOT_CATEGORIES:
        url = _wrap_rakuten_affiliate(cat["url"])
        cards += (
            f'<a href="{url}" target="_blank" rel="nofollow sponsored" '
            'style="flex:1;min-width:140px;text-decoration:none;'
            'background:linear-gradient(135deg,rgba(191,0,0,0.18),rgba(191,0,0,0.05));'
            'border:1px solid rgba(212,175,55,0.4);border-radius:10px;'
            'padding:0.8rem 0.6rem;text-align:center;color:#f4e4a1;'
            'transition:all 0.2s ease;">'
            f'<div style="font-size:1.6rem;">{cat["icon"]}</div>'
            f'<div style="font-size:0.85rem;font-weight:700;margin-top:0.2rem;">{cat["name"]}</div>'
            f'<div style="font-size:0.7rem;color:#c5c8d8;margin-top:0.15rem;">{cat["label"]}</div>'
            '</a>'
        )

    return (
        '<div style="background:linear-gradient(135deg,rgba(191,0,0,0.1),rgba(212,175,55,0.05));'
        'border:1px solid rgba(191,0,0,0.3);border-radius:14px;padding:1rem 1.2rem;margin:1rem 0;">'
        '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.7rem;">'
        '<div style="color:#bf0000;font-weight:700;font-size:0.9rem;letter-spacing:0.05em;">'
        '🛒 PR · Rakuten Affiliate'
        '</div>'
        '<div style="font-size:0.7rem;color:#9ca3c4;">楽天市場で今お得な商品</div>'
        '</div>'
        f'<div style="display:flex;gap:0.5rem;flex-wrap:wrap;">{cards}</div>'
        '</div>'
    )


def get_footer_banner_html() -> str:
    """フッター：楽天ジャンル別案内"""
    aff_id = _get("RAKUTEN_AFFILIATE_ID")
    if not aff_id:
        return (
            '<div class="ad-slot ad-banner">'
            '📢 PR枠 — フッター広告枠'
            '</div>'
        )

    genres = [
        ("📚 本・雑誌", "https://books.rakuten.co.jp/"),
        ("👗 ファッション", "https://search.rakuten.co.jp/search/mall/?g=100371"),
        ("🎮 ゲーム", "https://search.rakuten.co.jp/search/mall/?g=101205"),
        ("🏠 家電", "https://search.rakuten.co.jp/search/mall/?g=562637"),
        ("✨ コスメ", "https://search.rakuten.co.jp/search/mall/?g=100939"),
        ("🍴 食品", "https://search.rakuten.co.jp/search/mall/?g=100227"),
    ]

    cards = ""
    for label, url in genres:
        aff_url = _wrap_rakuten_affiliate(url)
        cards += (
            f'<a href="{aff_url}" target="_blank" rel="nofollow sponsored" '
            'style="text-decoration:none;color:#e8e8f0;'
            'background:rgba(212,175,55,0.08);'
            'border:1px solid rgba(212,175,55,0.25);'
            'border-radius:8px;padding:0.6rem 0.9rem;font-size:0.85rem;font-weight:500;'
            'transition:all 0.15s ease;">'
            f'{label}'
            '</a>'
        )

    return (
        '<div style="background:linear-gradient(135deg,rgba(191,0,0,0.08),rgba(212,175,55,0.03));'
        'border:1px solid rgba(212,175,55,0.25);border-radius:14px;padding:1.2rem 1.4rem;margin:1.5rem 0;text-align:center;">'
        '<div style="color:#bf0000;font-weight:700;font-size:0.85rem;margin-bottom:0.5rem;">'
        '🛒 PR · 楽天市場で探す'
        '</div>'
        '<div style="color:#c5c8d8;font-size:0.8rem;margin-bottom:0.9rem;">'
        '気になるジャンルで仕入れリサーチを始めよう'
        '</div>'
        f'<div style="display:flex;gap:0.5rem;flex-wrap:wrap;justify-content:center;">{cards}</div>'
        '</div>'
    )
