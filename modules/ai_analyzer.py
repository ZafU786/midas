"""
商品リサーチ・相場推定エンジン

優先順位（運営側で1個キーを設定すれば、サイト利用者は登録不要で使える）:
1. Gemini API + Google Search Grounding（無料枠 1500req/日、リアルタイム検索付き）
2. Pollinations.ai（完全無料・キー不要、検索なし）
3. Claude API（最終手段、有料）
"""
import json
import os
import re
import requests

# ----- バックエンド設定 -----
# gemini-2.5-flash-lite: 1日1000回まで無料（gemini-2.0-flashの200回より大幅に多い）
GEMINI_MODEL = "gemini-2.5-flash-lite"
GEMINI_FALLBACK = "gemini-2.0-flash"  # liteで失敗時のフォールバック
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"

POLLINATIONS_URL = "https://text.pollinations.ai/openai"
POLLINATIONS_MODEL = "openai"

CLAUDE_MODEL = "claude-haiku-4-5"


def _get_backend(user_key: str | None = None) -> str:
    """Geminiのみ対応"""
    if user_key or os.getenv("GEMINI_API_KEY"):
        return "gemini"
    raise RuntimeError("Gemini APIキーが必要です。サイドバーから入力してください。")


# ========================================================================
# JSON抽出ユーティリティ
# ========================================================================
def _extract_json(text: str):
    text = text.strip()
    if "```" in text:
        m = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
        if m:
            text = m.group(1).strip()
    arr_start = text.find("[")
    obj_start = text.find("{")
    if arr_start >= 0 and (obj_start < 0 or arr_start <= obj_start):
        end = text.rfind("]")
        if end > arr_start:
            return json.loads(text[arr_start:end + 1])
    if obj_start >= 0:
        end = text.rfind("}")
        if end > obj_start:
            return json.loads(text[obj_start:end + 1])
    raise ValueError(f"JSONが見つかりません。再試行してください。\n応答: {text[:200]}")


# ========================================================================
# Gemini + Google Search Grounding（推奨）
# ========================================================================
def _gemini_chat(prompt: str, max_tokens: int = 4000, use_search: bool = True, api_key: str | None = None) -> tuple[str, list[dict]]:
    """Geminiチャット。テキスト + 検索ソースURL一覧 を返す"""
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY が未設定")

    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.3,  # ハルシネーション抑制
            "maxOutputTokens": max_tokens,
        },
    }
    if use_search:
        body["tools"] = [{"google_search": {}}]

    last_err = None
    for model in (GEMINI_MODEL, GEMINI_FALLBACK):
        url = GEMINI_URL.format(model=model, key=key)
        r = requests.post(url, json=body, timeout=90)
        if r.status_code == 200:
            data = r.json()
            try:
                cand = data["candidates"][0]
                parts = cand["content"]["parts"]
                text = "\n".join(p.get("text", "") for p in parts if "text" in p)

                # Grounding URLを抽出（実際の検索結果のURL）
                grounding_urls = []
                gm = cand.get("groundingMetadata", {})
                for chunk in gm.get("groundingChunks", []):
                    web = chunk.get("web", {})
                    if web.get("uri"):
                        grounding_urls.append({
                            "uri": web["uri"],
                            "title": web.get("title", ""),
                        })
                return text, grounding_urls
            except (KeyError, IndexError) as e:
                last_err = f"応答パース失敗: {e} | {str(data)[:300]}"
                continue
        elif r.status_code == 429:
            raise RuntimeError(
                "🚫 Gemini APIの無料枠を使い切りました。\n\n"
                "対処方法:\n"
                "・数時間〜翌日まで待つ（無料枠は毎日リセット）\n"
                "・別のGoogleアカウントで新しいキーを発行\n"
                "・https://aistudio.google.com/app/apikey で確認"
            )
        else:
            last_err = f"{r.status_code}: {r.text[:200]}"
    raise RuntimeError(f"Gemini APIエラー: {last_err}")


# ========================================================================
# Pollinations.ai（フォールバック）
# ========================================================================
def _pollinations_chat(prompt: str, max_tokens: int = 3000) -> str:
    payload = {
        "model": POLLINATIONS_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.6,
        "max_tokens": max_tokens,
    }
    r = requests.post(POLLINATIONS_URL, json=payload, timeout=90)
    if r.status_code != 200:
        raise RuntimeError(f"Pollinations APIエラー {r.status_code}: {r.text[:200]}")
    return r.json()["choices"][0]["message"]["content"]


# ========================================================================
# Claude（オプション）
# ========================================================================
def _claude_chat(prompt: str, max_tokens: int = 3000) -> str:
    from anthropic import Anthropic
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    msg = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


# ========================================================================
# 統一エントリ
# ========================================================================
def _chat(prompt: str, max_tokens: int = 3000, use_search: bool = True, api_key: str | None = None):
    """Returns (text, grounding_urls)"""
    _get_backend(api_key)
    return _gemini_chat(prompt, max_tokens, use_search=use_search, api_key=api_key)


def has_valid_key(user_key: str | None = None) -> bool:
    """有効なAPIキーが設定されているか"""
    return bool(user_key or os.getenv("GEMINI_API_KEY"))


# 個別商品ページを示すURLパターン
PRODUCT_URL_PATTERNS = {
    "mercari": ["/item/m"],
    "auctions.yahoo": ["/auction/", "/jp/auction/"],
    "rakuten": ["/item/"],
    "amazon": ["/dp/", "/gp/product/"],
    "bookoff": ["/product/"],
    "fril": ["/items/"],
    "shopping.yahoo": ["/products/"],
}


def _is_product_page(uri: str, site_filter: str) -> bool:
    uri_low = uri.lower()
    if site_filter not in uri_low:
        return False
    patterns = PRODUCT_URL_PATTERNS.get(site_filter, [])
    return any(p in uri_low for p in patterns)


def _find_product_url(grounding_urls: list[dict], source_name: str, name: str) -> str:
    """grounding_urlsから個別商品ページを優先して抽出"""
    site_filter = {
        "メルカリ": "mercari",
        "ヤフオク即決": "auctions.yahoo",
        "ヤフオク": "auctions.yahoo",
        "楽天市場": "rakuten",
        "ラクマ": "fril",
        "ブックオフ": "bookoff",
        "Amazon": "amazon",
        "Yahoo!ショッピング": "shopping.yahoo",
    }.get(source_name, "")
    if not site_filter:
        return ""

    name_lower = name.lower()
    name_tokens = [t for t in name_lower.split() if len(t) >= 2]
    product_pages = []
    fallback_pages = []

    for g in grounding_urls:
        uri = g["uri"]
        title = g.get("title", "").lower()
        if site_filter not in uri.lower():
            continue
        score = sum(1 for t in name_tokens if t in title)
        if _is_product_page(uri, site_filter):
            product_pages.append((score, uri))
        else:
            fallback_pages.append((score, uri))

    if product_pages:
        product_pages.sort(reverse=True)
        return product_pages[0][1]
    if fallback_pages:
        fallback_pages.sort(reverse=True)
        return fallback_pages[0][1]
    return ""


# ========================================================================
# 1. AI商品提案
# ========================================================================
def suggest_products(category: str, budget_min: int, budget_max: int, count: int = 9, api_key: str | None = None) -> list[dict]:
    prompt = f"""あなたは日本のせどり・転売の専門家です。Google検索で実価格を確認しながら、
利益が出る商品を {count} 件提案してください。

【条件】
- カテゴリ: {category}
- 仕入予算: {budget_min}円 〜 {budget_max}円
- 必ず利益が出る（仕入値 + 手数料10% + 送料500円 < 販売価格）

【🔴 重要ルール: 仕入先と販売先は必ず別サイト】
- ✅ OK: メルカリで仕入れ → Amazonで販売
- ✅ OK: ヤフオク即決で仕入れ → メルカリで販売
- ❌ NG: メルカリ → メルカリ（同一サイト禁止）
- ❌ NG: ヤフオク即決 → ヤフオク即決（同一サイト禁止）
- buy_source と sell_platform は **必ず異なる** こと

【🔴 最重要：商品状態（コンディション）の一致】
商品の状態で値段が大きく変わるため、**必ず同じconditionで価格比較**すること:
- 仕入値（buy_price）と販売値（sell_price）は **同じcondition** で比較
- ✅ OK: メルカリ「中古-良」¥3000 ⇄ Amazon「中古-良」¥6000
- ❌ NG: メルカリ「ジャンク」¥500 ⇄ Amazon「新品」¥10000（状態違う）
- conditionが一致確認できない商品は提案しない

【🔴 絶対遵守】
1. **検索で確認できない価格は絶対に書かない**。推測・捏造は禁止。
2. **ヤフオクは即決(Buy It Now)のみ**。落札相場・入札中価格は使わない。
3. 「実際3万円なのに3500円」のような価格ズレは絶対NG。
4. 検索でヒットしない商品は提案しない（数を減らしてもよい）。

【検索手順】
1. メルカリ・ヤフオク即決で「{category}」を検索 → 安い出品を見つける
2. その商品の状態を確認（新品/中古-良/中古-可/ジャンク 等）
3. **同じ商品×同じ状態**でAmazon/メルカリ/ヤフオク即決を検索 → 売値を確認
4. 利益が確実に出るペアだけ採用

【出力】
JSON配列のみ。説明禁止。空なら `[]`。
各要素:
- name: 商品名・型番
- category: 細分カテゴリ
- condition: "新品" / "中古-良" / "中古-可" / "ジャンク" のいずれか★必須
- buy_price: 検索確認済み仕入価格（整数）
- buy_source: "メルカリ" / "ヤフオク即決" / "楽天市場" / "ラクマ" / "ブックオフ"
- sell_price: 同じ状態での販売相場（整数）
- sell_platform: "Amazon" / "メルカリ" / "ヤフオク即決"
- reason: 事実ベースの根拠（"メルカリ中古-良¥1500、Amazon中古-良¥3500" 等）
- risk: 注意点

出力例:
[{{"name":"SONY MDR-XB55","category":"イヤホン","condition":"中古-良","buy_price":1500,"buy_source":"メルカリ","sell_price":3500,"sell_platform":"Amazon","reason":"メルカリ中古-良が1500-2000円、Amazon中古-良が3500円前後","risk":"音漏れ・断線確認必須"}}]
"""
    text, grounding_urls = _chat(prompt, max_tokens=4000, use_search=True, api_key=api_key)
    items = _extract_json(text)

    # 同一サイト同士の提案を除外（AIが守らなかった場合の保険）
    def _norm(s: str) -> str:
        return (s or "").replace("即決", "").strip().lower()
    if isinstance(items, list):
        items = [it for it in items if _norm(it.get("buy_source", "")) != _norm(it.get("sell_platform", ""))]

    if grounding_urls and isinstance(items, list):
        for item in items:
            name = item.get("name", "")
            item["buy_url"] = _find_product_url(grounding_urls, item.get("buy_source", ""), name)
            item["sell_url"] = _find_product_url(grounding_urls, item.get("sell_platform", ""), name)
    return items


# ========================================================================
# 2. 単品分析
# ========================================================================
def analyze_product(name: str, buy_price: int | None = None, buy_source: str = "", api_key: str | None = None) -> dict:
    extra = ""
    if buy_price:
        extra += f"\n- 仕入予定価格: {buy_price}円"
    if buy_source:
        extra += f"\n- 仕入先: {buy_source}"

    prompt = f"""あなたは日本のせどり専門家です。Google検索で実際の出品・即決価格を確認して分析してください。

【商品】
- 名前: {name}{extra}

【絶対遵守】
- **検索で確認した価格のみ書く**。推測・捏造は禁止。
- **ヤフオクは即決（Buy It Now）のみ**。落札相場・オークション中の入札価格は使わない。
- 検索でヒットしなければ 0 とする。

【出力】
JSONオブジェクトのみ。説明禁止。

キー:
- name: 正規化商品名
- category: カテゴリ
- buy_price_estimate: メルカリ等の最低出品価格（整数）
- sell_amazon_estimate: Amazon中古相場（整数、不明なら0）
- sell_mercari_estimate: メルカリ相場（整数、不明なら0）
- sell_yahoo_estimate: ヤフオク**即決**相場のみ（落札相場禁止、整数、不明なら0）
- best_platform: 最も利益が出る販売先（"Amazon"/"メルカリ"/"ヤフオク即決"）
- demand: 需要（"高"/"中"/"低"）
- speed_label: 売れ行き（"1日以内"/"3日以内"/"5日以内"/"1週間以上"/"売れてない"）
- reason: 判定理由（検索で見た事実ベース）
- risk: 注意点
"""
    text, _ = _chat(prompt, max_tokens=2000, use_search=True, api_key=api_key)
    return _extract_json(text)


# ========================================================================
# 3. CSV一括分析
# ========================================================================
def batch_analyze(products: list[dict], api_key: str | None = None) -> list[dict]:
    items_text = "\n".join(
        f"{i+1}. {p.get('name', '')}"
        + (f" (仕入: {p['buy_price']}円)" if p.get("buy_price") else "")
        for i, p in enumerate(products)
    )
    prompt = f"""日本のせどり専門家として、以下{len(products)}件を分析。

【商品】
{items_text}

【出力】
JSON配列のみ（長さ={len(products)}）。説明禁止。
キー: name, category, buy_price_estimate, sell_amazon_estimate, sell_mercari_estimate,
      sell_yahoo_estimate, best_platform, demand, speed_label, reason, risk
（demand: 高/中/低, speed_label: 1日以内/3日以内/5日以内/1週間以上/売れてない,
  best_platform: Amazon/メルカリ/ヤフオク）
"""
    # 一括分析は検索なし（コスト節約）
    text, _ = _chat(prompt, max_tokens=6000, use_search=False, api_key=api_key)
    return _extract_json(text)
