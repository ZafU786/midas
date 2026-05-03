"""
CSV保存・読込モジュール
仕入れ候補リストと利益商品リストをCSVで管理する
"""

import os
from datetime import datetime
import pandas as pd

# データ保存先
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CANDIDATES_PATH = os.path.join(DATA_DIR, "candidates.csv")
DEALS_PATH = os.path.join(DATA_DIR, "deals.csv")

# 候補リストのカラム定義
CANDIDATES_COLUMNS = [
    "id",
    "商品名",
    "仕入れ価格",
    "仕入れ元",
    "仕入れ元URL",
    "カテゴリ",
    "AIスコア",
    "AI判定理由",
    "登録日時",
    "お気に入り",
]

# 利益商品リストのカラム定義
DEALS_COLUMNS = [
    "id",
    "商品名",
    "仕入れ価格",
    "仕入れ元",
    "仕入れ元URL",
    "販売価格",
    "販売プラットフォーム",
    "手数料",
    "送料",
    "その他経費",
    "純利益",
    "利益率",
    "売れ行き",
    "判定",
    "AIスコア",
    "登録日時",
    "お気に入り",
]


def _ensure_data_dir():
    """dataディレクトリが存在しなければ作成する"""
    os.makedirs(DATA_DIR, exist_ok=True)


def load_candidates() -> pd.DataFrame:
    """仕入れ候補CSVを読み込む。ファイルがなければ空DataFrameを返す"""
    _ensure_data_dir()
    if os.path.exists(CANDIDATES_PATH):
        return pd.read_csv(CANDIDATES_PATH, encoding="utf-8-sig")
    return pd.DataFrame(columns=CANDIDATES_COLUMNS)


def load_deals() -> pd.DataFrame:
    """利益商品CSVを読み込む。ファイルがなければ空DataFrameを返す"""
    _ensure_data_dir()
    if os.path.exists(DEALS_PATH):
        return pd.read_csv(DEALS_PATH, encoding="utf-8-sig")
    return pd.DataFrame(columns=DEALS_COLUMNS)


def save_candidates(df: pd.DataFrame) -> None:
    """仕入れ候補DataFrameをCSVに保存する"""
    _ensure_data_dir()
    df.to_csv(CANDIDATES_PATH, index=False, encoding="utf-8-sig")


def save_deals(df: pd.DataFrame) -> None:
    """利益商品DataFrameをCSVに保存する"""
    _ensure_data_dir()
    df.to_csv(DEALS_PATH, index=False, encoding="utf-8-sig")


def add_candidate(item: dict) -> pd.DataFrame:
    """
    候補商品を1件追加して保存する

    Args:
        item: 商品情報の辞書（CANDIDATES_COLUMNSのキーを含む）

    Returns:
        更新後のDataFrame
    """
    df = load_candidates()
    item.setdefault("id", _generate_id(df))
    item.setdefault("登録日時", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    item.setdefault("お気に入り", False)

    new_row = pd.DataFrame([item])
    df = pd.concat([df, new_row], ignore_index=True)
    save_candidates(df)
    return df


def add_deal(item: dict) -> pd.DataFrame:
    """
    利益商品を1件追加して保存する

    Args:
        item: 商品情報の辞書（DEALS_COLUMNSのキーを含む）

    Returns:
        更新後のDataFrame
    """
    df = load_deals()
    item.setdefault("id", _generate_id(df))
    item.setdefault("登録日時", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    item.setdefault("お気に入り", False)

    new_row = pd.DataFrame([item])
    df = pd.concat([df, new_row], ignore_index=True)
    save_deals(df)
    return df


def toggle_favorite(df: pd.DataFrame, item_id: int, path: str) -> pd.DataFrame:
    """
    お気に入りフラグを切り替えてCSVに保存する

    Args:
        df: 対象DataFrame
        item_id: 切り替え対象のid
        path: 保存先パス（CANDIDATES_PATH or DEALS_PATH）

    Returns:
        更新後のDataFrame
    """
    mask = df["id"] == item_id
    df.loc[mask, "お気に入り"] = ~df.loc[mask, "お気に入り"].astype(bool)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return df


def export_deals_csv(sort_by: str = "純利益") -> bytes:
    """
    利益商品リストをCSVバイト列として返す（Streamlitのダウンロードボタン用）

    Args:
        sort_by: ソートキー（"純利益" / "利益率" / "売れ行き"）

    Returns:
        UTF-8 with BOM のCSVバイト列
    """
    df = load_deals()
    if sort_by in df.columns:
        df = df.sort_values(sort_by, ascending=False)
    return df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")


def clear_candidates() -> None:
    """仕入れ候補リストをリセットする"""
    save_candidates(pd.DataFrame(columns=CANDIDATES_COLUMNS))


def _generate_id(df: pd.DataFrame) -> int:
    """DataFrameの最大idの次の値を返す"""
    if df.empty or "id" not in df.columns:
        return 1
    return int(df["id"].max()) + 1
