"""
出品文章生成モジュール
Claude APIでメルカリ用のタイトル・説明文・ハッシュタグを自動生成する
"""

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """あなたはメルカリ出品のプロです。
売れる商品タイトルと説明文を作成することに長けています。
指示通りのフォーマットで出力してください。"""

USER_PROMPT_TEMPLATE = """以下の商品のメルカリ出品用コンテンツを作成してください。

商品名：{name}
商品の状態：{condition}

以下の形式で出力してください：

【タイトル】
（40文字以内で魅力的に。検索されやすいキーワードを含める）

【説明文】
（3〜5文で商品の魅力・状態・注意点を記載）

【ハッシュタグ】
#タグ1 #タグ2 #タグ3 #タグ4 #タグ5"""


def generate_listing(name: str, condition: str) -> dict:
    """
    出品用テキストを生成する

    Args:
        name: 商品名
        condition: 商品の状態（例：「未使用」「美品」「傷あり」）

    Returns:
        {"title": str, "description": str, "hashtags": str, "error": str | None}
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return {"title": "", "description": "", "hashtags": "", "error": "ANTHROPIC_API_KEY が設定されていません"}

    client = anthropic.Anthropic(api_key=api_key)
    prompt = USER_PROMPT_TEMPLATE.format(name=name, condition=condition)

    try:
        message = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text.strip()
        return _parse_output(raw)

    except anthropic.AuthenticationError:
        return {"title": "", "description": "", "hashtags": "", "error": "APIキーが無効です"}
    except anthropic.RateLimitError:
        return {"title": "", "description": "", "hashtags": "", "error": "レート制限に達しました。しばらく待ってください"}
    except Exception as e:
        return {"title": "", "description": "", "hashtags": "", "error": str(e)[:100]}


def _parse_output(text: str) -> dict:
    """AIの出力テキストをタイトル・説明文・ハッシュタグに分割する"""
    result = {"title": "", "description": "", "hashtags": "", "error": None}

    lines = text.split("\n")
    current_section = None
    buffer = []

    for line in lines:
        stripped = line.strip()
        if "【タイトル】" in stripped:
            current_section = "title"
            buffer = []
        elif "【説明文】" in stripped:
            if current_section == "title" and buffer:
                result["title"] = " ".join(buffer).strip()[:40]
            current_section = "description"
            buffer = []
        elif "【ハッシュタグ】" in stripped:
            if current_section == "description" and buffer:
                result["description"] = "\n".join(buffer).strip()
            current_section = "hashtags"
            buffer = []
        elif stripped and current_section:
            buffer.append(stripped)

    # 最後のセクションを確定
    if current_section == "hashtags" and buffer:
        result["hashtags"] = " ".join(buffer).strip()
    elif current_section == "description" and buffer:
        result["description"] = "\n".join(buffer).strip()

    return result
