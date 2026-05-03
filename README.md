# 👑 MIDAS — The Ultimate Reselling Oracle

AI（Google Gemini）でせどり・転売の利益商品を自動リサーチするツール。

メルカリ・ヤフオク・Amazon・楽天など複数ECサイトを横断検索し、利益が出る商品を提示します。

## 🌟 主な機能

- **AI商品提案**: カテゴリと予算を指定するだけでAIが利益商品を提案
- **単品分析**: 商品名から各サイトの相場と最適な販売先を判定
- **CSV一括分析**: 大量の商品リストをまとめてAI判定
- **利益自動計算**: 手数料・送料込みの純利益を即座に算出
- **8ECサイト対応**: 楽天・メルカリ・ヤフオク・Amazon・ラクマ・ブックオフ等

## 🚀 起動方法（ローカル）

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

ブラウザで http://localhost:8501 を開く。

## 🔑 APIキー

サイドバーから **Google Gemini APIキー** を入力してください。

無料・1日1500回まで利用可能・クレカ不要：
👉 https://aistudio.google.com/app/apikey

## ⚠️ 免責事項

本サービスはAIによる相場推定ツールです。
表示される価格は目安であり、実際の取引価格を保証するものではありません。
仕入れ前に必ず実際のサイトで価格・在庫・状態をご確認ください。
取引の判断と結果の責任はすべてユーザー様にあります。

## 📜 ライセンス

個人利用・商用利用可。
