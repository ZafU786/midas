"""
基盤モジュールの動作確認用テスト
APIキー不要で実行可能。

実行: python test_basic.py
"""

from modules import profit_calc, csv_handler, mercari_helper


def test_profit_calc():
    print("=== 利益計算テスト ===")
    r = profit_calc.calc_profit(
        sell_price=4000, buy_price=2000,
        platform="メルカリ", shipping=200,
    )
    print(f"  売価4000 / 仕入2000 / 送料200 / メルカリ")
    print(f"  → 手数料: ¥{r['fee_amount']}, 純利益: ¥{r['net_profit']}, 利益率: {r['profit_rate']}%")
    assert r["fee_amount"] == 400
    assert r["net_profit"] == 1400
    print("  ✅ OK\n")

    print("=== 判定テスト ===")
    v1 = profit_calc.get_verdict(net_profit=1500, speed_label="3日以内")
    print(f"  利益1500 + 3日以内 → {v1['emoji']} {v1['verdict']}")
    assert v1["verdict"] == "BUY!"

    v2 = profit_calc.get_verdict(net_profit=700, speed_label="1週間以上")
    print(f"  利益700 + 1週間以上 → {v2['emoji']} {v2['verdict']}")
    assert v2["verdict"] == "検討"

    v3 = profit_calc.get_verdict(net_profit=300, speed_label="売れてない")
    print(f"  利益300 + 売れてない → {v3['emoji']} {v3['verdict']}")
    assert v3["verdict"] == "スキップ"
    print("  ✅ OK\n")


def test_mercari_helper():
    print("=== メルカリURL生成テスト ===")
    url = mercari_helper.build_search_url("Anker モバイルバッテリー")
    print(f"  {url}")
    assert "jp.mercari.com" in url
    assert "status=sold_out" in url
    print("  ✅ OK\n")


def test_csv_handler():
    print("=== CSVハンドラテスト ===")
    item = {
        "商品名": "テスト商品",
        "仕入れ価格": 1500,
        "仕入れ元": "楽天",
        "仕入れ元URL": "https://example.com",
        "カテゴリ": "テスト",
        "AIスコア": 75,
        "AI判定理由": "テストデータです",
    }
    df = csv_handler.add_candidate(item)
    print(f"  追加後の候補数: {len(df)}")
    assert len(df) >= 1
    print("  ✅ OK\n")

    # クリーンアップ
    csv_handler.clear_candidates()


if __name__ == "__main__":
    test_profit_calc()
    test_mercari_helper()
    test_csv_handler()
    print("🎉 全テスト合格！")
