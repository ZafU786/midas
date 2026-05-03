"""
Claude APIを使った売れ筋判定モジュール
商品情報を渡してメルカリでの売れる可能性をスコア化する
"""

import json
import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

# スコアの閾値（これ以上の商品だけを候補リストに表示）
SCORE_THRESHOLD = 60

SYSTEM_PROMPT = """あなたはメルカリ物販のプロです。
日本のメルカリ市場に精通しており、何が売れるか・売れないかを的確に判断できます。
必ずJSON形式のみで返答し、それ以外のテキストは一切出力しないでください。"""

USER_PROMPT_TEMPLATE = """以下の商品がメルカリで売れる可能性をスコア化してください。

商品名：{name}
仕入れ価格：{price}円
カテゴリ：{category}

評価基準：
- メルカリでの需要（検索されやすいか）
- 価格帯の適切さ（仕入れ価格より高く売れる余地があるか）
- 回転率の高さ（すぐ売れるか）
- ブランド・シリーズの知名度

以下のJSON形式のみで返答してください：
{{"score": 0から100の整数, "reason": "判定理由を1文で（日本語）"}}"""


def score_item(name: str, price: int, category: str) -> dict:
    """
    1商品の売れ筋スコアをClaude APIで算出する

    Args:
        name: 商品名
        price: 仕入れ価格（円）
        category: カテゴリ名

    Returns:
        {"score": int, "reason": str}
        エラー時は {"score": 0, "reason": "エラーメッセージ"}
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return {"score": 0, "reason": "ANTHROPIC_API_KEY が設定されていません"}

    client = anthropic.Anthropic(api_key=api_key)

    prompt = USER_PROMPT_TEMPLATE.format(
        name=name,
        price=price,
        category=category,
    )

    try:
        message = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=256,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text.strip()
        result = json.loads(raw)

        # 型チェック
        score = int(result.get("score", 0))
        reason = str(result.get("reason", ""))
        return {"score": max(0, min(100, score)), "reason": reason}

    except json.JSONDecodeError:
        return {"score": 0, "reason": f"AIの返答を解析できませんでした: {raw[:50]}"}
    except anthropic.AuthenticationError:
        return {"score": 0, "reason": "APIキーが無効です。設定画面を確認してください。"}
    except anthropic.RateLimitError:
        return {"score": 0, "reason": "APIのレート制限に達しました。しばらく待ってから再試行してください。"}
    except Exception as e:
        return {"score": 0, "reason": f"AI判定中にエラーが発生しました: {str(e)[:80]}"}


def filter_items(items: list[dict], threshold: int = SCORE_THRESHOLD) -> list[dict]:
    """
    商品リストをAIでスコアリングし、閾値以上のみ返す

    Args:
        items: 商品情報の辞書リスト（search APIの返り値）
        threshold: 通過スコアの下限

    Returns:
        スコアリング済みの商品リスト（threshold以上のみ）
    """
    scored = []
    for item in items:
        result = score_item(
            name=item.get("商品名", ""),
            price=item.get("仕入れ価格", 0),
            category=item.get("カテゴリ", ""),
        )
        item["AIスコア"] = result["score"]
        item["AI判定理由"] = result["reason"]
        if result["score"] >= threshold:
            scored.append(item)

    return sorted(scored, key=lambda x: x["AIスコア"], reverse=True)
