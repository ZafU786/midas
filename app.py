"""
物販リサーチツール（プレミアム版）
- AIによる商品提案・分析
- ECサイト直リンク
- AI生成商品イメージ
- ダーク × ゴールド高級UI
"""
import os
import html
from pathlib import Path
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

from modules import ai_analyzer, profit_calc, csv_handler, links

ENV_PATH = Path(__file__).parent / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH, override=True)

# Streamlit Cloudの secrets を環境変数にマージ（アフィリエイトタグ等）
try:
    for _k, _v in st.secrets.items():
        if isinstance(_v, str) and _k not in os.environ:
            os.environ[_k] = _v
except Exception:
    pass  # secrets未設定の環境ではスキップ

# ========== ページ設定 ==========
st.set_page_config(
    page_title="MIDAS | 究極のせどりインテリジェンス",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ========== プレミアムCSS ==========
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&family=Cormorant+Garamond:wght@500;700&family=Inter:wght@400;500;600;700&display=swap');

    /* 全体ベース：深いネイビー × ゴールド */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #151a3a 50%, #1a1f4a 100%);
        color: #e8e8f0;
        font-family: 'Inter', 'Noto Sans JP', sans-serif;
    }
    .main .block-container {
        padding-top: 2rem;
        max-width: 1400px;
    }

    /* ヘッダーロゴ */
    .premium-hero {
        text-align: center;
        padding: 2.5rem 0 1.5rem 0;
        border-bottom: 1px solid rgba(212, 175, 55, 0.2);
        margin-bottom: 2rem;
    }
    .premium-hero h1 {
        font-family: 'Cormorant Garamond', serif;
        font-size: 5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #d4af37 0%, #fef3a8 30%, #d4af37 50%, #fef3a8 70%, #b8932d 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: 0.18em;
        margin: 0;
        text-shadow: 0 0 60px rgba(212, 175, 55, 0.3);
        line-height: 1;
    }
    .premium-hero .hero-emblem {
        color: rgba(212, 175, 55, 0.5);
        font-size: 1.2rem;
        letter-spacing: 0.5em;
        margin-bottom: 0.6rem;
    }
    .premium-hero .subtitle {
        color: #d4af37;
        font-size: 0.85rem;
        letter-spacing: 0.4em;
        text-transform: uppercase;
        margin-top: 0.8rem;
        font-weight: 500;
    }
    .premium-hero .hero-tagline {
        color: #e8e8f0;
        font-size: 1.1rem;
        font-weight: 500;
        margin-top: 0.6rem;
        letter-spacing: 0.05em;
    }

    /* バリュープロポジション */
    .value-prop {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.2rem;
        margin: 1.5rem 0 2rem 0;
    }
    .value-card {
        background: linear-gradient(135deg, rgba(212, 175, 55, 0.08) 0%, rgba(255,255,255,0.02) 100%);
        border: 1px solid rgba(212, 175, 55, 0.25);
        border-radius: 14px;
        padding: 1.4rem 1.2rem;
        text-align: center;
    }
    .value-card .icon { font-size: 2rem; margin-bottom: 0.5rem; }
    .value-card .title {
        color: #f4e4a1;
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 0.4rem;
    }
    .value-card .desc {
        color: #c5c8d8;
        font-size: 0.85rem;
        line-height: 1.6;
    }

    /* 信頼性数値 */
    .credibility-bar {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        background: linear-gradient(135deg, rgba(212, 175, 55, 0.12) 0%, rgba(212, 175, 55, 0.03) 100%);
        border: 1px solid rgba(212, 175, 55, 0.3);
        border-radius: 14px;
        padding: 1.2rem;
        margin: 1rem 0 2rem 0;
    }
    .cred-item { text-align: center; }
    .cred-num {
        font-family: 'Cormorant Garamond', serif;
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #d4af37 0%, #f4e4a1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
    }
    .cred-label {
        color: #c5c8d8;
        font-size: 0.78rem;
        margin-top: 0.3rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    /* 広告枠 */
    .ad-slot {
        background: linear-gradient(135deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.01) 100%);
        border: 1px dashed rgba(212, 175, 55, 0.3);
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        margin: 1.5rem 0;
        color: #9ca3c4;
        font-size: 0.85rem;
    }
    .ad-slot.ad-banner { min-height: 90px; display: flex; align-items: center; justify-content: center; }
    .ad-slot.ad-square { min-height: 250px; display: flex; align-items: center; justify-content: center; flex-direction: column; }

    /* セクションヘッダー */
    .section-header {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.8rem;
        color: #f4e4a1;
        margin: 2rem 0 0.5rem 0;
        text-align: center;
        letter-spacing: 0.05em;
    }
    .section-sub {
        text-align: center;
        color: #c5c8d8;
        font-size: 0.9rem;
        margin-bottom: 1.5rem;
        letter-spacing: 0.03em;
    }

    /* タブ */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255,255,255,0.03);
        border-radius: 14px;
        padding: 6px;
        gap: 4px;
        border: 1px solid rgba(212, 175, 55, 0.15);
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 10px;
        padding: 10px 24px;
        color: #9ca3c4;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(212, 175, 55, 0.2), rgba(212, 175, 55, 0.05));
        color: #f4e4a1 !important;
        border: 1px solid rgba(212, 175, 55, 0.3);
    }

    /* ボタン */
    .stButton > button {
        background: linear-gradient(135deg, #d4af37 0%, #b8932d 100%);
        color: #0a0e27;
        border: none;
        border-radius: 10px;
        padding: 0.6em 1.6em;
        font-weight: 600;
        letter-spacing: 0.05em;
        box-shadow: 0 4px 14px rgba(212, 175, 55, 0.25);
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #f4e4a1 0%, #d4af37 100%);
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(212, 175, 55, 0.4);
    }

    /* 入力欄：白背景 × 黒文字でハッキリ見える */
    .stTextInput input, .stNumberInput input {
        background: #ffffff !important;
        border: 2px solid rgba(212, 175, 55, 0.4) !important;
        border-radius: 10px !important;
        color: #0a0e27 !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        padding: 0.6rem 0.9rem !important;
    }
    .stSelectbox > div > div {
        background: #ffffff !important;
        border: 2px solid rgba(212, 175, 55, 0.4) !important;
        border-radius: 10px !important;
        color: #0a0e27 !important;
        font-weight: 600 !important;
    }
    .stSelectbox > div > div * {
        color: #0a0e27 !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #d4af37 !important;
        box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.25) !important;
    }
    /* ラベルはゴールドで濃く */
    label, .stSelectbox label, .stNumberInput label, .stTextInput label,
    [data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p {
        color: #f4e4a1 !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.03em;
    }
    /* number input のステッパーボタン */
    .stNumberInput button {
        background: #f4e4a1 !important;
        color: #0a0e27 !important;
    }
    /* file uploader */
    [data-testid="stFileUploader"] section {
        background: rgba(255,255,255,0.95) !important;
        border: 2px dashed rgba(212, 175, 55, 0.4) !important;
        border-radius: 10px !important;
    }
    [data-testid="stFileUploader"] section * {
        color: #0a0e27 !important;
    }
    /* checkbox */
    .stCheckbox label, .stCheckbox p {
        color: #e8e8f0 !important;
    }

    /* サイドバー */
    [data-testid="stSidebar"] {
        background: rgba(10, 14, 39, 0.95);
        border-right: 1px solid rgba(212, 175, 55, 0.15);
    }
    [data-testid="stSidebar"] .stMarkdown {
        color: #e8e8f0;
    }

    /* === コンパクト商品カード（pc-*） === */
    .pc {
        background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%);
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: 14px;
        overflow: hidden;
        margin-bottom: 1rem;
        transition: all 0.25s ease;
    }
    .pc:hover {
        border-color: rgba(212, 175, 55, 0.5);
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    }
    .pc-img {
        width: 100%;
        height: 160px;
        object-fit: cover;
        display: block;
        background: #0a0e27;
    }
    .pc-body { padding: 0.9rem 1rem 1rem 1rem; }
    .pc-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    .pc-cat {
        font-size: 0.72rem;
        color: #9ca3c4;
        letter-spacing: 0.05em;
    }
    .pc-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #f4e4a1;
        line-height: 1.35;
        margin-bottom: 0.7rem;
        min-height: 2.6em;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .pc-prices {
        display: grid;
        grid-template-columns: 1fr 1.2fr 1fr;
        align-items: center;
        padding: 0.7rem 0;
        border-top: 1px solid rgba(212, 175, 55, 0.15);
        border-bottom: 1px solid rgba(212, 175, 55, 0.15);
        margin-bottom: 0.8rem;
    }
    .pc-pcell { padding: 0 0.2rem; }
    .pc-center { text-align: center; }
    .pc-right { text-align: right; }
    .pc-plabel {
        font-size: 0.65rem;
        color: #9ca3c4;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.2rem;
    }
    .pc-pval {
        font-size: 0.95rem;
        font-weight: 600;
        color: #e8e8f0;
    }
    .pc-profit {
        font-size: 1.25rem;
        font-weight: 700;
        line-height: 1.1;
    }
    /* CTA：仕入・販売の大きなボタン */
    .pc-cta {
        display: block;
        text-align: center;
        padding: 0.65rem 0.8rem;
        border-radius: 10px;
        font-size: 0.85rem;
        font-weight: 700;
        text-decoration: none !important;
        margin-bottom: 0.4rem;
        transition: all 0.15s ease;
    }
    .pc-cta:last-child { margin-bottom: 0; }
    .pc-cta-buy {
        background: linear-gradient(135deg, #d4af37 0%, #b8932d 100%);
        color: #0a0e27 !important;
        border: 1px solid #d4af37;
    }
    .pc-cta-buy:hover {
        background: linear-gradient(135deg, #f4e4a1 0%, #d4af37 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(212, 175, 55, 0.4);
    }
    .pc-cta-sell {
        background: rgba(212, 175, 55, 0.08);
        color: #f4e4a1 !important;
        border: 1px solid rgba(212, 175, 55, 0.4);
    }
    .pc-cta-sell:hover {
        background: rgba(212, 175, 55, 0.18);
        border-color: #d4af37;
    }

    /* 旧スタイル（互換用） */
    .product-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.01) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(212, 175, 55, 0.15);
        border-radius: 16px;
        padding: 0;
        margin-bottom: 1.5rem;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    .product-card:hover {
        border-color: rgba(212, 175, 55, 0.4);
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.4);
    }
    .product-card-img {
        width: 100%;
        height: 220px;
        object-fit: cover;
        background: #0a0e27;
    }
    .product-card-body { padding: 1.2rem 1.4rem; }
    .product-card-title {
        font-size: 1.05rem;
        font-weight: 600;
        color: #e8e8f0;
        margin: 0 0 0.4rem 0;
        line-height: 1.4;
    }
    .product-card-meta {
        font-size: 0.78rem;
        color: #9ca3c4;
        margin-bottom: 0.8rem;
        letter-spacing: 0.03em;
    }
    .product-card-price-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.7rem 0;
        border-top: 1px solid rgba(212, 175, 55, 0.1);
        border-bottom: 1px solid rgba(212, 175, 55, 0.1);
        margin-bottom: 0.8rem;
    }
    .price-label {
        font-size: 0.72rem;
        color: #9ca3c4;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    .price-value { font-size: 1rem; font-weight: 600; color: #e8e8f0; }
    .price-profit { font-size: 1.4rem; font-weight: 700; }
    .profit-positive {
        color: #d4af37;
        background: linear-gradient(135deg, #d4af37 0%, #f4e4a1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .profit-negative { color: #ef4444; }

    /* ECサイトリンクボタン */
    .link-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 0.4rem;
        margin-top: 0.8rem;
    }
    .link-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.3rem;
        padding: 0.5rem 0.6rem;
        background: rgba(212, 175, 55, 0.08);
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: 8px;
        color: #e8e8f0 !important;
        text-decoration: none !important;
        font-size: 0.78rem;
        font-weight: 500;
        transition: all 0.15s ease;
    }
    .link-btn:hover {
        background: rgba(212, 175, 55, 0.18);
        border-color: rgba(212, 175, 55, 0.5);
        text-decoration: none !important;
    }

    /* バッジ */
    .verdict-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.05em;
    }
    .verdict-buy {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.2), rgba(34, 197, 94, 0.05));
        color: #4ade80;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }
    .verdict-check {
        background: linear-gradient(135deg, rgba(212, 175, 55, 0.2), rgba(212, 175, 55, 0.05));
        color: #fbbf24;
        border: 1px solid rgba(212, 175, 55, 0.3);
    }
    .verdict-skip {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(239, 68, 68, 0.05));
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }

    /* DataFrame */
    [data-testid="stDataFrame"] {
        background: rgba(255,255,255,0.02);
        border-radius: 12px;
        border: 1px solid rgba(212, 175, 55, 0.15);
    }

    /* メトリクス */
    [data-testid="stMetricValue"] {
        font-family: 'Cormorant Garamond', serif !important;
        font-size: 2.2rem !important;
        background: linear-gradient(135deg, #d4af37 0%, #f4e4a1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    [data-testid="stMetricLabel"] { color: #9ca3c4 !important; }

    /* セクションタイトル */
    h2, h3 {
        color: #f4e4a1;
        letter-spacing: 0.03em;
        font-weight: 600;
    }
    .section-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.3), transparent);
        margin: 2rem 0;
    }

    /* alert系 */
    .stAlert { border-radius: 12px; }

    /* スクロールバー */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
    ::-webkit-scrollbar-thumb {
        background: rgba(212, 175, 55, 0.3);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover { background: rgba(212, 175, 55, 0.5); }

    /* Streamlitの邪魔な要素を非表示 */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ========== ヒーローセクション ==========
st.markdown(
    """
    <div class="premium-hero">
        <div class="hero-emblem">⟢ ⋄ ⟣</div>
        <h1>MIDAS</h1>
        <div class="subtitle">THE ULTIMATE RESELLING ORACLE</div>
        <div class="hero-tagline">触れた商品を、すべて利益に変える</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ========== サイドバー（先に描画してuser_keyを取得） ==========
with st.sidebar:
    st.markdown("### 🔑  Gemini APIキー")

    user_key_input = st.text_input(
        "APIキーを入力",
        type="password",
        value=st.session_state.get("user_gemini_key", ""),
        placeholder="AIza...",
        help="無料・1日1500回まで利用可能",
    )
    if user_key_input:
        st.session_state["user_gemini_key"] = user_key_input.strip()

    user_key = st.session_state.get("user_gemini_key", "")

    if user_key:
        st.success("🟢 接続済み")
    else:
        st.error("⚠️ キー未設定")

    if st.button("📖  使い方ガイドを見る", use_container_width=True):
        st.session_state["show_guide"] = not st.session_state.get("show_guide", False)
        st.session_state["show_legal"] = False
        st.rerun()

    if st.button("📜  利用規約・プライバシー", use_container_width=True):
        st.session_state["show_legal"] = not st.session_state.get("show_legal", False)
        st.session_state["show_guide"] = False
        st.rerun()

    st.markdown("---")
    st.markdown("### ⚙️  詳細設定")
    min_profit = st.number_input("最低利益額（円）", value=500, step=100)
    default_shipping = st.number_input("デフォルト送料（円）", value=350, step=50)
    show_images = st.checkbox("AI商品画像を表示", value=True, help="Pollinations AIで生成（無料）")

    st.markdown("---")
    st.markdown("### 📊 Stats")
    df_saved = csv_handler.load_deals()
    st.metric("保存済み商品", f"{len(df_saved)}")
    if not df_saved.empty:
        total_profit = df_saved["純利益"].sum() if "純利益" in df_saved.columns else 0
        st.metric("想定総利益", f"¥{int(total_profit):,}")

    st.markdown("---")
    # サイドバー：楽天デイリーランキング誘導
    _aff = os.getenv("RAKUTEN_AFFILIATE_ID", "")
    if _aff:
        import urllib.parse as _up
        _target = _up.quote("https://ranking.rakuten.co.jp/daily/", safe="")
        _aff_url = f"https://hb.afl.rakuten.co.jp/hgc/{_aff}/?pc={_target}&m={_target}"
        st.markdown(
            f'<a href="{_aff_url}" target="_blank" rel="nofollow sponsored" '
            'style="display:block;text-decoration:none;'
            'background:linear-gradient(135deg,rgba(191,0,0,0.18),rgba(212,175,55,0.05));'
            'border:1px solid rgba(212,175,55,0.4);border-radius:12px;'
            'padding:1rem;text-align:center;color:#f4e4a1;">'
            '<div style="font-size:0.7rem;color:#bf0000;font-weight:700;letter-spacing:0.1em;">PR · 楽天</div>'
            '<div style="font-size:1.8rem;margin:0.3rem 0;">👑</div>'
            '<div style="font-weight:700;font-size:0.95rem;color:#f4e4a1;">デイリーランキング</div>'
            '<div style="font-size:0.75rem;color:#c5c8d8;margin-top:0.3rem;">今売れてる商品をチェック</div>'
            '</a>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="ad-slot ad-square">'
            '<div style="font-size:1.5rem;">📢</div>'
            '<div style="margin-top:0.5rem;font-weight:600;color:#f4e4a1;">PR枠</div>'
            '<div style="margin-top:0.4rem;font-size:0.75rem;">アフィID未設定</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown(
        """
        <div style="font-size:0.78rem;color:#9ca3c4;line-height:1.7;">
        <b style="color:#f4e4a1;">💡 使い方</b><br>
        1. カテゴリと予算を選ぶ<br>
        2. AIに提案させる<br>
        3. 各サイトへのリンクから出品<br>
        ━━━━━━━━━━━━━━<br>
        <b style="color:#f4e4a1;">⚠️ 免責事項</b><br>
        相場推定はAIによる目安です。<br>
        実際の価格は必ずご確認ください。
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==============================================================================
# 利用規約・プライバシーポリシーページ
# ==============================================================================
if st.session_state.get("show_legal", False):
    st.markdown(
        '<h2 style="text-align:center;color:#f4e4a1;font-family:Cormorant Garamond,serif;font-size:2.3rem;letter-spacing:0.1em;margin-bottom:0.3rem;">LEGAL</h2>'
        '<div style="text-align:center;color:#c5c8d8;margin-bottom:2rem;">利用規約・プライバシーポリシー</div>',
        unsafe_allow_html=True,
    )
    if st.button("← トップへ戻る", key="back_legal_top"):
        st.session_state["show_legal"] = False
        st.rerun()

    st.markdown(
        """
<style>
.legal-section {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(212, 175, 55, 0.2);
    border-radius: 12px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1rem;
    color: #e8e8f0;
    line-height: 1.8;
}
.legal-section h3 {
    color: #f4e4a1;
    font-size: 1.15rem;
    margin: 0 0 0.6rem 0;
}
.legal-section h4 {
    color: #d4af37;
    font-size: 0.95rem;
    margin: 1rem 0 0.4rem 0;
}
.legal-section p, .legal-section li {
    color: #c5c8d8;
    font-size: 0.9rem;
}
</style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="legal-section">
<h3>📜 利用規約</h3>

<h4>第1条（サービス概要）</h4>
<p>MIDAS（以下「本サービス」）は、AI（Google Gemini API）を用いて、せどり・転売目的の商品リサーチ支援機能を提供するウェブツールです。</p>

<h4>第2条（利用方法）</h4>
<p>利用者は、自身で取得したGoogle Gemini APIキーを入力することで本サービスを利用できます。APIキーは利用者のブラウザセッション内のみで保持され、当サーバーには保存されません。</p>

<h4>第3条（禁止事項）</h4>
<ul>
<li>法令または公序良俗に反する行為</li>
<li>本サービスの運営を妨害する行為</li>
<li>不正なAPIキーの使用、または他者のキーを無断で使用すること</li>
<li>本サービスを利用した違法商品・規制商品の取引</li>
</ul>

<h4>第4条（免責事項）</h4>
<p>本サービスが表示する価格・需要・利益額等の情報は、AIによる<b>推定値</b>であり、正確性・完全性・最新性を保証するものではありません。実際の取引に関する判断および結果については、すべて利用者の自己責任となります。</p>
<p>本サービスの利用によって生じたいかなる損害（仕入れた商品が売れない、想定より安く売れた、出品先のアカウント停止等）についても、運営者は一切の責任を負いません。</p>

<h4>第5条（サービス変更・停止）</h4>
<p>運営者は、利用者への事前通知なく、本サービスの内容を変更・停止する場合があります。</p>

<h4>第6条（広告・アフィリエイト）</h4>
<p>本サービスはアフィリエイト広告および第三者広告（Google AdSense等）を掲載することがあります。リンク先での取引については、各サイトの利用規約に従ってください。</p>
</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="legal-section">
<h3>🔒 プライバシーポリシー</h3>

<h4>1. 収集する情報</h4>
<p>本サービスは、利用者から以下の情報を取得することがあります：</p>
<ul>
<li>アクセスログ（IPアドレス・ブラウザ情報・アクセス日時）</li>
<li>Cookie（広告配信および利用状況分析のため）</li>
<li>利用者が入力した検索条件・商品名（AI処理のためGoogleに送信）</li>
</ul>
<p><b>APIキーはブラウザセッション内でのみ保持され、サーバーへは送信されません。</b></p>

<h4>2. 情報の利用目的</h4>
<ul>
<li>本サービスの提供および機能改善</li>
<li>不正利用の防止</li>
<li>広告配信の最適化</li>
</ul>

<h4>3. 第三者への提供</h4>
<p>以下の第三者サービスに対し、必要最小限の情報を送信することがあります：</p>
<ul>
<li><b>Google Gemini API</b> — 商品名・カテゴリ等の検索クエリ</li>
<li><b>Pollinations.ai</b> — 商品名（画像生成プロンプト用）</li>
<li><b>Google AdSense / アフィリエイト ASP</b> — Cookieによる広告配信</li>
</ul>

<h4>4. Cookieの使用</h4>
<p>本サービスはGoogleアナリティクス・AdSense等のCookieを使用することがあります。ブラウザ設定からCookieを無効化することで利用を拒否できますが、一部機能が制限される場合があります。</p>

<h4>5. お問い合わせ</h4>
<p>本ポリシーに関するお問い合わせは、運営者までご連絡ください。</p>

<h4>6. 改定</h4>
<p>本ポリシーは予告なく改定されることがあります。改定後の内容は本ページに掲載した時点で効力を生じます。</p>
</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div style="text-align:center;color:#9ca3c4;font-size:0.85rem;margin-top:2rem;">'
        '最終更新: 2026年5月 / © MIDAS'
        '</div>',
        unsafe_allow_html=True,
    )

    if st.button("← トップへ戻る", key="back_legal_bottom", use_container_width=True):
        st.session_state["show_legal"] = False
        st.rerun()
    st.stop()


# ==============================================================================
# 使い方ガイドページ（ボタンで切替表示）
# ==============================================================================
if st.session_state.get("show_guide", False):
    st.markdown(
        """
<style>
.guide-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.04), rgba(255,255,255,0.01));
    border: 1px solid rgba(212, 175, 55, 0.25);
    border-radius: 14px;
    padding: 1.6rem 1.8rem;
    margin-bottom: 1.2rem;
}
.guide-step-num {
    display: inline-block;
    width: 36px; height: 36px; line-height: 36px;
    text-align: center;
    background: linear-gradient(135deg, #d4af37, #b8932d);
    color: #0a0e27;
    border-radius: 50%;
    font-weight: 700;
    font-size: 1.1rem;
    margin-right: 0.8rem;
    vertical-align: middle;
}
.guide-step-title {
    color: #f4e4a1;
    font-size: 1.2rem;
    font-weight: 700;
    display: inline-block;
    vertical-align: middle;
}
.guide-step-body {
    color: #e8e8f0;
    font-size: 0.95rem;
    line-height: 1.8;
    margin-top: 0.7rem;
    padding-left: 3rem;
}
.guide-step-body code {
    background: rgba(212,175,55,0.12);
    color: #f4e4a1;
    padding: 0.1rem 0.4rem;
    border-radius: 4px;
    font-size: 0.9rem;
}
.guide-tag {
    display: inline-block;
    padding: 0.2rem 0.7rem;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
    margin-right: 0.4rem;
    background: rgba(212, 175, 55, 0.15);
    color: #f4e4a1;
    border: 1px solid rgba(212, 175, 55, 0.4);
}
.faq-q {
    color: #f4e4a1;
    font-weight: 700;
    margin-top: 0.8rem;
    font-size: 1rem;
}
.faq-a {
    color: #c5c8d8;
    font-size: 0.9rem;
    line-height: 1.7;
    margin-bottom: 1rem;
}
</style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<h2 style="text-align:center;color:#f4e4a1;font-family:Cormorant Garamond,serif;font-size:2.5rem;letter-spacing:0.1em;margin-bottom:0.3rem;">USER GUIDE</h2>'
        '<div style="text-align:center;color:#c5c8d8;margin-bottom:2rem;">MIDAS の使い方を3分で理解する</div>',
        unsafe_allow_html=True,
    )

    if st.button("← トップへ戻る", key="back_top"):
        st.session_state["show_guide"] = False
        st.rerun()

    # ▼ STEP 1
    st.markdown(
        '<div class="guide-card">'
        '<span class="guide-step-num">1</span>'
        '<span class="guide-step-title">Gemini APIキーを取得（2分・完全無料）</span>'
        '<div class="guide-step-body">'
        '<span class="guide-tag">必須</span><span class="guide-tag">クレカ不要</span><span class="guide-tag">1日1500回まで無料</span><br><br>'
        'MIDASはGoogleの<b>Gemini AI</b>を使って商品リサーチをします。'
        'キーは<b>あなた専用</b>で、Googleアカウントから無料発行できます。<br><br>'
        '<b>取得手順:</b><br>'
        '① <a href="https://aistudio.google.com/app/apikey" target="_blank" style="color:#f4e4a1;">Google AI Studioを開く</a><br>'
        '② Googleアカウントでログイン<br>'
        '③ 画面の「<code>Create API key</code>」をクリック<br>'
        '④ 「<code>Create API key in new project</code>」を選択<br>'
        '⑤ 発行された <code>AIza...</code> で始まるキーをコピー<br>'
        '⑥ <b>このサイトのサイドバー「APIキーを入力」欄にペースト</b><br><br>'
        '<i>※キーはあなたのブラウザ内のみに保存され、サーバーには送信されません。</i>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ▼ STEP 2
    st.markdown(
        '<div class="guide-card">'
        '<span class="guide-step-num">2</span>'
        '<span class="guide-step-title">「AI商品提案」で利益商品を発掘</span>'
        '<div class="guide-step-body">'
        '<span class="guide-tag">基本機能</span><br><br>'
        '一番カンタンな使い方。<b>カテゴリと予算を選ぶだけ</b>で、AIが利益の出る商品を提案します。<br><br>'
        '<b>使い方:</b><br>'
        '① タブ「🔍 AI商品提案」を選択<br>'
        '② <b>カテゴリ</b>を選ぶ（本／家電／ファッション など10種類）<br>'
        '③ <b>予算下限・上限</b>を入力（例: 500〜3000円）<br>'
        '④ <b>提案数</b>を選ぶ（推奨: 5〜9件）<br>'
        '⑤ 「🚀 AI提案」をクリック → 30秒〜1分待つ<br>'
        '⑥ 利益額順にカードが表示される<br><br>'
        '<b>カードの見方:</b><br>'
        '・<span style="color:#4ade80;">🟢 BUY!</span> = 利益1000円以上の推奨商品<br>'
        '・<span style="color:#fbbf24;">🟡 検討</span> = 微妙な商品<br>'
        '・<span style="color:#f87171;">🔴 スキップ</span> = 利益なし<br>'
        '・「🛒 ○○で買う」ボタン → 仕入先サイトでその商品を検索<br>'
        '・「💰 ○○で売る」ボタン → 販売先サイトを開く'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ▼ STEP 3
    st.markdown(
        '<div class="guide-card">'
        '<span class="guide-step-num">3</span>'
        '<span class="guide-step-title">「単品分析」で具体的な商品を調べる</span>'
        '<div class="guide-step-body">'
        '<span class="guide-tag">深掘り用</span><br><br>'
        'すでに気になる商品がある時にこちら。商品名を入れると、<b>Amazon・メルカリ・ヤフオクの3つの相場を比較</b>してくれます。<br><br>'
        '<b>使い方:</b><br>'
        '① タブ「🎯 単品分析」を選択<br>'
        '② <b>商品名・型番</b>を入力（例: <code>SONY WH-1000XM4</code>）<br>'
        '③ （任意）仕入価格・仕入先も入力できる<br>'
        '④ 「🔬 分析」をクリック<br>'
        '⑤ 3つのカードでどこで売るのが一番儲かるか一目で分かる<br><br>'
        '<b>こんな時に使う:</b><br>'
        '・店頭で見つけた商品が利益出るかその場で確認<br>'
        '・メルカリで安く出品されてる商品を仕入れるか判断<br>'
        '・どのプラットフォームで売れば一番高いか調べる'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ▼ STEP 4
    st.markdown(
        '<div class="guide-card">'
        '<span class="guide-step-num">4</span>'
        '<span class="guide-step-title">「CSV一括分析」で大量商品を判定</span>'
        '<div class="guide-step-body">'
        '<span class="guide-tag">上級者向け</span><br><br>'
        '商品リストをまとめてAIに判定させる機能。100件くらいまで一気に処理できます。<br><br>'
        '<b>使い方:</b><br>'
        '① ExcelやメモでCSVを作る:<br>'
        '<code>商品名,仕入れ価格<br>SONY WH-1000XM4,3000<br>Nintendo Switch,15000</code><br>'
        '② タブ「📥 CSV一括分析」を選択<br>'
        '③ ファイルをアップロード → 「🚀 一括分析」<br>'
        '④ 利益順にソートされた結果がカードで出る<br>'
        '⑤ CSVダウンロードで結果保存可'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ▼ STEP 5
    st.markdown(
        '<div class="guide-card">'
        '<span class="guide-step-num">5</span>'
        '<span class="guide-step-title">「保存リスト」で気になる商品を管理</span>'
        '<div class="guide-step-body">'
        '<span class="guide-tag">便利機能</span><br><br>'
        '各タブで「💾 保存」ボタンを押すと、商品が「💎 保存リスト」タブに溜まります。<br><br>'
        '<b>できること:</b><br>'
        '・販売先で絞り込み（Amazonだけ表示など）<br>'
        '・最低利益額でフィルタ<br>'
        '・純利益／利益率／登録日でソート<br>'
        '・CSV出力で外部管理'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ▼ FAQ
    st.markdown(
        '<div class="guide-card">'
        '<span class="guide-step-num">?</span>'
        '<span class="guide-step-title">よくある質問</span>'
        '<div class="guide-step-body">'
        '<div class="faq-q">Q. 本当に無料ですか？</div>'
        '<div class="faq-a">はい。Geminiの無料枠（1日1500回）の範囲内で完全無料です。'
        '個人利用ならまず超えません。クレカ登録も不要です。</div>'

        '<div class="faq-q">Q. APIキーの安全性は？</div>'
        '<div class="faq-a">キーはあなたのブラウザ内（セッションストレージ）のみに保存され、'
        '当サイトのサーバーには一切送信されません。'
        'AIへのリクエストは直接Googleのサーバーへ送られます。</div>'

        '<div class="faq-q">Q. AIの提示する価格は正確？</div>'
        '<div class="faq-a">Gemini + Google検索でリアルタイム価格を取得しますが、'
        '<b>あくまで目安</b>です。仕入れ前に必ず実際のサイトで価格と在庫を確認してください。</div>'

        '<div class="faq-q">Q. 何の商品を仕入れていいか分からない</div>'
        '<div class="faq-a">「🔍 AI商品提案」タブでカテゴリと予算を入れるだけでAIが提案します。'
        '初心者の方はまず「本」「500〜2000円」あたりから試してみてください。</div>'

        '<div class="faq-q">Q. 仕入れた商品が売れなかった場合の責任は？</div>'
        '<div class="faq-a">本サイトはAIによる相場推定ツールです。'
        '実取引の判断と結果の責任はすべてユーザー様にあります。'
        '少額から始めることを強くおすすめします。</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ▼ せどりの基礎知識
    st.markdown(
        '<div class="guide-card">'
        '<span class="guide-step-num">★</span>'
        '<span class="guide-step-title">せどり初心者へ：押さえるべき基礎</span>'
        '<div class="guide-step-body">'
        '<b>1. 利益の式</b><br>'
        '<code>純利益 = 販売価格 −（仕入価格 + 手数料 + 送料 + その他経費）</code><br>'
        'プラットフォーム手数料は約10%、送料は350〜800円が目安。<br><br>'

        '<b>2. プラットフォーム別の特徴</b><br>'
        '・<b>Amazon</b>: 高単価・回転速い・FBA手数料が高い<br>'
        '・<b>メルカリ</b>: 個人取引・小物向け・手数料10%<br>'
        '・<b>ヤフオク</b>: マニア向け・古いものが高く売れる<br>'
        '・<b>ラクマ</b>: 手数料6%（最安）だが客層は狭い<br><br>'

        '<b>3. 失敗しないコツ</b><br>'
        '・初回は<b>2000円以下の商品</b>から始める（リスク低）<br>'
        '・<b>需要が安定したジャンル</b>を選ぶ（古本・中古ゲーム等）<br>'
        '・<b>複数サイトで相場確認</b>してから仕入れる（MIDASがやってくれる）<br>'
        '・売れない期間も想定して<b>キャッシュフロー</b>に余裕を'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    if st.button("← トップへ戻る", key="back_bottom", use_container_width=True):
        st.session_state["show_guide"] = False
        st.rerun()

    st.stop()  # ガイド表示中は通常UIを描画しない


# （APIキー未設定時のゲートは、バリュー紹介セクション後で実施 → 後段で）

# ========== トップ広告枠：楽天アフィリエイト ==========
st.markdown(links.get_top_banner_html(), unsafe_allow_html=True)

# ========== APIキーゲート ==========
if not user_key:
    st.markdown(
        """
<div style="background:linear-gradient(135deg,rgba(212,175,55,0.15),rgba(212,175,55,0.03));
            border:2px solid rgba(212,175,55,0.5);
            border-radius:16px;padding:2.2rem;text-align:center;margin:1rem 0;">
<div style="font-size:3rem;">🔑</div>
<h2 style="color:#f4e4a1;margin:0.5rem 0;font-size:1.6rem;">START FREE — Gemini APIキーを設定</h2>
<p style="color:#e8e8f0;font-size:1rem;margin:1rem 0;line-height:1.7;">
<b>完全無料</b>・1日1500回まで利用可能・<b>クレカ登録不要</b><br>
たった2分で取得できます
</p>
<div style="background:rgba(0,0,0,0.25);padding:1.3rem;border-radius:10px;margin:1.2rem auto;text-align:left;max-width:520px;">
<b style="color:#f4e4a1;font-size:1rem;">取得手順:</b><br>
<span style="color:#e8e8f0;line-height:2.1;font-size:0.95rem;">
① <a href="https://aistudio.google.com/app/apikey" target="_blank" style="color:#f4e4a1;font-weight:700;text-decoration:underline;">Google AI Studio を開く ▶</a><br>
② Googleアカウントでログイン<br>
③ 「Create API key」をクリック<br>
④ 発行された <code style="background:rgba(212,175,55,0.15);padding:0.1rem 0.4rem;border-radius:4px;color:#f4e4a1;">AIza...</code> で始まるキーをコピー<br>
⑤ <b>左サイドバー「APIキーを入力」欄にペースト</b>
</span>
</div>
<p style="color:#9ca3c4;font-size:0.85rem;margin-top:1rem;">
🔒 キーはあなたのブラウザにのみ保存され、当サーバーには送信されません
</p>
</div>
        """,
        unsafe_allow_html=True,
    )
    st.info("📖 詳しい使い方は左サイドバーの「使い方ガイドを見る」を押してください")
    st.stop()


# ========== カードレンダリング関数 ==========
def render_product_card(item: dict, show_img: bool = True):
    """商品カード（画像 + 利益 + 仕入/販売リンク）。
    NOTE: markdownはインデントをコードブロック扱いするので、HTMLは
    必ず行頭から書く（インデントしない）。
    """
    name_raw = str(item.get("name", ""))
    name = html.escape(name_raw)
    category = html.escape(str(item.get("category", "")))
    condition = html.escape(str(item.get("condition", "")))
    buy_price = item.get("buy_price", 0)
    sell_price = item.get("sell_price", 0)
    profit = item.get("profit", 0)
    profit_rate = item.get("profit_rate", 0)
    buy_source = html.escape(str(item.get("buy_source", "")))
    sell_platform = html.escape(str(item.get("sell_platform", "")))
    verdict = item.get("verdict", "検討")

    verdict_class = {"BUY!": "verdict-buy", "検討": "verdict-check", "スキップ": "verdict-skip"}.get(verdict, "verdict-check")
    profit_class = "profit-positive" if profit >= 0 else "profit-negative"
    sign = "+" if profit >= 0 else ""

    img_html = ""
    if show_img and name_raw:
        img_url = links.get_image_url(name_raw)
        img_html = f'<img class="pc-img" src="{img_url}" loading="lazy" onerror="this.style.display=\'none\'" />'

    # 仕入先・販売先のURL（AIが返した実URL優先、なければ検索URLにフォールバック）
    search_urls = links.get_search_urls(name_raw)
    buy_url = item.get("buy_url") or search_urls.get(item.get("buy_source", ""), search_urls.get("楽天市場", "#"))
    sell_url = item.get("sell_url") or search_urls.get(item.get("sell_platform", ""), search_urls.get("メルカリ", "#"))

    # 行頭から書く（インデント禁止）
    card = (
        '<div class="pc">'
        f'{img_html}'
        '<div class="pc-body">'
        f'<div class="pc-top"><span class="verdict-badge {verdict_class}">{verdict}</span><span class="pc-cat">{category}{" · " + condition if condition else ""}</span></div>'
        f'<div class="pc-title">{name}</div>'
        '<div class="pc-prices">'
        f'<div class="pc-pcell"><div class="pc-plabel">仕入</div><div class="pc-pval">¥{buy_price:,}</div></div>'
        f'<div class="pc-pcell pc-center"><div class="pc-plabel">利益</div><div class="pc-profit {profit_class}">{sign}¥{profit:,}</div><div class="pc-plabel">{profit_rate}%</div></div>'
        f'<div class="pc-pcell pc-right"><div class="pc-plabel">販売</div><div class="pc-pval">¥{sell_price:,}</div></div>'
        '</div>'
        f'<a href="{buy_url}" target="_blank" class="pc-cta pc-cta-buy">🛒 {buy_source}で買う</a>'
        f'<a href="{sell_url}" target="_blank" class="pc-cta pc-cta-sell">💰 {sell_platform}で売る</a>'
        '</div>'
        '</div>'
    )
    return card


# ========== タブ ==========
tab1, tab2, tab3, tab4 = st.tabs(
    ["🔍  AI商品提案", "🎯  単品分析", "📥  CSV一括分析", "💎  保存リスト"]
)


# ========== TAB 1: AI商品提案 ==========
with tab1:
    st.markdown("### AIにせどり候補を提案させる")
    st.caption("カテゴリと予算を指定すると、Claude AIが利益の出そうな商品を提案します")

    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
    with col1:
        category = st.selectbox(
            "カテゴリ",
            ["本", "家電", "ファッション", "コスメ", "おもちゃ", "ゲーム", "ホビー/フィギュア", "アクセサリー", "スポーツ用品", "その他"],
        )
    with col2:
        budget_min = st.number_input("予算下限", value=500, step=100, key="b_min")
    with col3:
        budget_max = st.number_input("予算上限", value=5000, step=100, key="b_max")
    with col4:
        count = st.number_input("提案数", value=9, min_value=3, max_value=20, step=1)
    with col5:
        st.markdown("<br>", unsafe_allow_html=True)
        run_suggest = st.button("🚀  AI提案", key="suggest_btn", use_container_width=True)

    if run_suggest:
        spinner_msg = "🔎 Web検索付きで分析中... (20〜40秒)" if user_key else "🔎 簡易AIが分析中... (10〜20秒)"
        with st.spinner(spinner_msg):
            try:
                results = ai_analyzer.suggest_products(category, budget_min, budget_max, count, api_key=user_key or None)
                st.session_state["suggestions"] = results
            except Exception as e:
                st.error(f"エラー: {e}")

    if "suggestions" in st.session_state:
        results = st.session_state["suggestions"]
        st.markdown(f"##### ✅  {len(results)}件の提案 ")
        st.warning(
            "⚠️ **AI推定価格です。** 仕入れ前に必ずリンク先で実際の価格・在庫を確認してください。"
            "AIは検索結果から推定するため、誤差や情報遅延が発生することがあります。",
            icon="⚠️",
        )

        cards_data = []
        for r in results:
            # 新スキーマ: buy_price/sell_price (Web検索結果)
            # 旧互換: buy_price_estimate/sell_price_estimate
            buy = r.get("buy_price") or r.get("buy_price_estimate", 0)
            sell = r.get("sell_price") or r.get("sell_price_estimate", 0)
            calc = profit_calc.calc_profit(
                sell_price=sell, buy_price=buy,
                platform=r.get("sell_platform", "メルカリ"),
                shipping=default_shipping,
            )
            verdict = profit_calc.get_verdict(calc["net_profit"], "3日以内", min_profit)
            cards_data.append({
                "name": r.get("name", ""),
                "category": r.get("category", ""),
                "condition": r.get("condition", ""),
                "buy_price": buy,
                "sell_price": sell,
                "profit": calc["net_profit"],
                "profit_rate": calc["profit_rate"],
                "buy_source": r.get("buy_source", ""),
                "sell_platform": r.get("sell_platform", ""),
                "buy_url": r.get("buy_url", ""),
                "sell_url": r.get("sell_url", ""),
                "verdict": verdict["verdict"],
                "reason": r.get("reason", ""),
                "risk": r.get("risk", ""),
            })

        # 利益順
        cards_data.sort(key=lambda x: x["profit"], reverse=True)

        # 3列グリッド
        for i in range(0, len(cards_data), 3):
            cols = st.columns(3)
            for j, c in enumerate(cards_data[i:i+3]):
                with cols[j]:
                    st.markdown(render_product_card(c, show_images), unsafe_allow_html=True)

        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            df = pd.DataFrame(cards_data)
            csv = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
            st.download_button("📥  CSVダウンロード", csv, "ai_suggestions.csv", "text/csv", use_container_width=True)
        with col_b:
            if st.button("💾  全件を保存リストに追加", use_container_width=True):
                for c in cards_data:
                    csv_handler.add_deal({
                        "商品名": c["name"],
                        "仕入れ価格": c["buy_price"],
                        "仕入れ元": c["buy_source"],
                        "仕入れ元URL": links.get_search_urls(c["name"]).get(c["buy_source"], ""),
                        "販売価格": c["sell_price"],
                        "販売プラットフォーム": c["sell_platform"],
                        "手数料": int(c["sell_price"] * 0.1),
                        "送料": default_shipping,
                        "その他経費": 0,
                        "純利益": c["profit"],
                        "利益率": c["profit_rate"],
                        "売れ行き": "3日以内",
                        "判定": c["verdict"],
                        "AIスコア": "",
                    })
                st.success("保存しました")


# ========== TAB 2: 単品分析 ==========
with tab2:
    st.markdown("### 商品名から相場と利益を分析")
    st.caption("Amazon・メルカリ・ヤフオクの想定相場をAIが推定します")

    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    with col1:
        product_name = st.text_input("商品名・型番", placeholder="例: SONY WH-1000XM4")
    with col2:
        buy_price_input = st.number_input("仕入価格（任意）", value=0, step=100)
    with col3:
        buy_source_input = st.text_input("仕入先", placeholder="ブックオフ等")
    with col4:
        st.markdown("<br>", unsafe_allow_html=True)
        run_analyze = st.button("🔬  分析", use_container_width=True)

    if run_analyze:
        if not product_name.strip():
            st.warning("商品名を入力してください")
        else:
            spinner_msg2 = "🔎 Web検索付きで分析中..." if user_key else "🔎 簡易AIが分析中..."
            with st.spinner(spinner_msg2):
                try:
                    result = ai_analyzer.analyze_product(
                        product_name,
                        buy_price=buy_price_input or None,
                        buy_source=buy_source_input or "",
                        api_key=user_key or None,
                    )
                    st.session_state["analyze_result"] = result
                except Exception as e:
                    st.error(f"エラー: {e}")

    if "analyze_result" in st.session_state:
        r = st.session_state["analyze_result"]

        # ヒーロー部分（画像 + 商品名）
        col_img, col_info = st.columns([1, 2])
        with col_img:
            if show_images:
                img_url = links.get_image_url(r.get("name", ""), 500, 400)
                st.image(img_url, use_container_width=True)
        with col_info:
            st.markdown(f"### {html.escape(r.get('name', ''))}")
            st.markdown(
                f"<div class='product-card-meta'>"
                f"カテゴリ: <b>{html.escape(r.get('category', ''))}</b> &nbsp; • &nbsp; "
                f"需要: <b>{html.escape(r.get('demand', ''))}</b> &nbsp; • &nbsp; "
                f"売れ行き: <b>{html.escape(r.get('speed_label', ''))}</b>"
                f"</div>", unsafe_allow_html=True,
            )
            st.markdown(f"**🏆 推奨販売先:** {html.escape(r.get('best_platform', ''))}")
            st.markdown(f"**💡 判定理由:** {html.escape(r.get('reason', ''))}")
            st.markdown(f"**⚠️ リスク:** {html.escape(r.get('risk', ''))}")

        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

        # 仕入れの最安URLを大きく表示
        buy = r.get("buy_price_estimate", 0)
        buy_url_real = r.get("buy_url", "")
        buy_source_real = r.get("buy_source", "")
        if buy_url_real:
            st.markdown(
                f'<a href="{buy_url_real}" target="_blank" class="pc-cta pc-cta-buy" style="display:block;margin-bottom:1rem;font-size:1rem;padding:0.9rem;">🛒 最安で仕入れる: {html.escape(buy_source_real)} ¥{buy:,}</a>',
                unsafe_allow_html=True,
            )

        # 3プラットフォーム比較（URL付き）
        platforms = [
            ("Amazon", r.get("sell_amazon_estimate", 0), r.get("sell_amazon_url", "") or links.get_search_urls(r.get("name", ""))["Amazon"]),
            ("メルカリ", r.get("sell_mercari_estimate", 0), r.get("sell_mercari_url", "") or links.get_search_urls(r.get("name", ""))["メルカリ"]),
            ("ヤフオク", r.get("sell_yahoo_estimate", 0), r.get("sell_yahoo_url", "") or links.get_search_urls(r.get("name", ""))["ヤフオク"]),
        ]
        cols = st.columns(3)
        for i, (plat, sell, plat_url) in enumerate(platforms):
            calc = profit_calc.calc_profit(
                sell_price=sell, buy_price=buy, platform=plat, shipping=default_shipping
            )
            with cols[i]:
                profit_color = "#d4af37" if calc["net_profit"] >= 0 else "#f87171"
                card_html = (
                    f'<a href="{plat_url}" target="_blank" style="text-decoration:none;">'
                    f'<div class="pc" style="padding:1.2rem;margin-bottom:0;">'
                    f'<div class="pc-plabel">{plat}で売る</div>'
                    f'<div style="font-size:1.6rem;font-weight:700;color:{profit_color};margin:0.4rem 0;">¥{calc["net_profit"]:+,}</div>'
                    f'<div style="font-size:0.8rem;color:#c5c8d8;">相場 ¥{sell:,} / 手数料 ¥{calc["fee_amount"]:,}<br>利益率 {calc["profit_rate"]}%</div>'
                    f'<div style="margin-top:0.5rem;font-size:0.75rem;color:#d4af37;">→ {plat}を見る</div>'
                    f'</div></a>'
                )
                st.markdown(card_html, unsafe_allow_html=True)

        platforms_dict = {p[0]: p[1] for p in platforms}

        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

        if st.button("💾  保存リストに追加", key="save_single"):
            best = r.get("best_platform", "メルカリ")
            best_calc = profit_calc.calc_profit(
                sell_price=platforms_dict.get(best, 0), buy_price=buy, platform=best, shipping=default_shipping
            )
            csv_handler.add_deal({
                "商品名": r.get("name", ""),
                "仕入れ価格": buy,
                "仕入れ元": r.get("buy_source", buy_source_input),
                "仕入れ元URL": r.get("buy_url", ""),
                "販売価格": platforms_dict.get(best, 0),
                "販売プラットフォーム": best,
                "手数料": best_calc["fee_amount"],
                "送料": default_shipping,
                "その他経費": 0,
                "純利益": best_calc["net_profit"],
                "利益率": best_calc["profit_rate"],
                "売れ行き": r.get("speed_label", ""),
                "判定": "",
                "AIスコア": r.get("demand", ""),
            })
            st.success("保存しました")


# ========== TAB 3: CSV一括分析 ==========
with tab3:
    st.markdown("### CSV一括分析")
    st.caption("商品名一覧のCSVをアップロードすると、AIがまとめて相場・利益を判定します")

    with st.expander("📋  CSVフォーマット例"):
        st.code("商品名,仕入れ価格\nSONY WH-1000XM4,15000\nNintendo Switch,25000\n", language="csv")

    uploaded = st.file_uploader("CSVファイルを選択", type=["csv"])
    if uploaded is not None:
        df_in = pd.read_csv(uploaded, encoding="utf-8-sig")
        st.write(f"📋  {len(df_in)}件読み込み")
        st.dataframe(df_in.head(), use_container_width=True)

        if st.button("🚀  一括分析を実行", type="primary"):
            products = []
            for _, row in df_in.iterrows():
                p = {"name": str(row.iloc[0])}
                if len(row) > 1 and pd.notna(row.iloc[1]):
                    try:
                        p["buy_price"] = int(row.iloc[1])
                    except (ValueError, TypeError):
                        pass
                products.append(p)

            with st.spinner(f"✨ AIが{len(products)}件を分析中..."):
                try:
                    results = ai_analyzer.batch_analyze(products, api_key=user_key or None)
                    st.session_state["batch_results"] = results
                except Exception as e:
                    st.error(f"エラー: {e}")

    if "batch_results" in st.session_state:
        results = st.session_state["batch_results"]
        cards_data = []
        for r in results:
            buy = r.get("buy_price_estimate", 0)
            best = r.get("best_platform", "メルカリ")
            sell_key = {"Amazon": "sell_amazon_estimate", "メルカリ": "sell_mercari_estimate", "ヤフオク": "sell_yahoo_estimate"}.get(best, "sell_mercari_estimate")
            sell = r.get(sell_key, 0)
            calc = profit_calc.calc_profit(sell_price=sell, buy_price=buy, platform=best, shipping=default_shipping)
            verdict = profit_calc.get_verdict(calc["net_profit"], r.get("speed_label", "3日以内"), min_profit)
            cards_data.append({
                "name": r.get("name", ""),
                "category": r.get("category", ""),
                "buy_price": buy,
                "sell_price": sell,
                "profit": calc["net_profit"],
                "profit_rate": calc["profit_rate"],
                "buy_source": "市場相場",
                "sell_platform": best,
                "verdict": verdict["verdict"],
                "reason": r.get("reason", ""),
            })
        cards_data.sort(key=lambda x: x["profit"], reverse=True)

        for i in range(0, len(cards_data), 3):
            cols = st.columns(3)
            for j, c in enumerate(cards_data[i:i+3]):
                with cols[j]:
                    st.markdown(render_product_card(c, show_images), unsafe_allow_html=True)

        df_out = pd.DataFrame(cards_data)
        csv = df_out.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button("📥  CSVダウンロード", csv, "batch_results.csv", "text/csv")


# ========== TAB 4: 保存リスト ==========
with tab4:
    st.markdown("### 保存済み商品")

    df_deals = csv_handler.load_deals()
    if df_deals.empty:
        st.info("まだ保存された商品がありません。")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_platform = st.multiselect(
                "販売先で絞り込み",
                options=df_deals["販売プラットフォーム"].dropna().unique().tolist(),
            )
        with col2:
            min_profit_filter = st.number_input("利益額(以上)", value=0, step=100)
        with col3:
            sort_key = st.selectbox("ソート", ["純利益", "利益率", "登録日時"])

        df_view = df_deals.copy()
        if filter_platform:
            df_view = df_view[df_view["販売プラットフォーム"].isin(filter_platform)]
        df_view = df_view[df_view["純利益"] >= min_profit_filter]
        if sort_key in df_view.columns:
            df_view = df_view.sort_values(sort_key, ascending=False)

        st.write(f"📊  {len(df_view)}件 / 全{len(df_deals)}件")
        st.dataframe(df_view, use_container_width=True, height=400)

        col_a, col_b = st.columns(2)
        with col_a:
            csv = csv_handler.export_deals_csv(sort_by=sort_key)
            st.download_button("📥  CSVダウンロード", csv, "deals.csv", "text/csv", use_container_width=True)
        with col_b:
            if st.button("🗑️  全件削除", use_container_width=True):
                csv_handler.save_deals(pd.DataFrame(columns=csv_handler.DEALS_COLUMNS))
                st.rerun()


# ========== フッター広告：楽天ジャンル別 ==========
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown(links.get_footer_banner_html(), unsafe_allow_html=True)

# ========== 「使い方」セクション ==========
st.markdown('<div class="section-header">USE CASES</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">こんなせどらーに使われています</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="value-prop">
        <div class="value-card">
            <div class="icon">📚</div>
            <div class="title">本せどり</div>
            <div class="desc">ブックオフで仕入れた本がAmazonでいくらで売れるか即判定。プレミア本の見逃しゼロへ。</div>
        </div>
        <div class="value-card">
            <div class="icon">🎮</div>
            <div class="title">ゲーム・ホビー</div>
            <div class="desc">レトロゲーム、絶版フィギュア、限定品の相場をAIが推定。仕入れ前に利益を可視化。</div>
        </div>
        <div class="value-card">
            <div class="icon">👗</div>
            <div class="title">ブランド古着</div>
            <div class="desc">メルカリ→ラクマ、Yahoo!→Amazonなど、最も高く売れる販路をAIが提案。</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ========== フッター ==========
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown(
    """
    <div style="text-align:center;color:#9ca3c4;padding:2rem 0;">
        <div style="font-family:'Cormorant Garamond',serif;font-size:1.8rem;color:#d4af37;letter-spacing:0.2em;">MIDAS</div>
        <div style="font-size:0.8rem;letter-spacing:0.2em;margin-top:0.4rem;">THE ULTIMATE RESELLING ORACLE</div>
        <div style="margin-top:1.2rem;font-size:0.75rem;line-height:1.8;">
            © 2026 MIDAS. Powered by Google Gemini &amp; Pollinations AI.<br>
            本サービスはAIによる相場推定ツールです。実取引の最終判断はご自身でお願いします。<br>
            <span style="color:#d4af37;">サイドバーから 利用規約・プライバシーポリシー をご確認ください</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
