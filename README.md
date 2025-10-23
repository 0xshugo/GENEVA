# GENEVA – Generative Ethics Validator

GENEVA（Generative Ethics Validator）は、生成コンテンツの倫理面をサポートするためのテキストおよび画像類似度チェッカーです。AIによる繰り返しの検出や、画像のpHash比較など、教育・研究・クリエイティブ制作のワークフローを支援します。本READMEは**ソフトウェア自体の説明書**であり、以下で触れるMITライセンス文とは役割が異なります。

## 特徴
- **テキスト検査**: TF-IDFコサイン類似度を用いた文章比較と、AIリピティションスコアによる繰り返し判定。
- **画像検査**: 離散コサイン変換（DCT）を利用したpHash類似度計算で、視覚的に近い画像を抽出。
- **Streamlit UI**: 「Text Check」「Image Check」のタブを備えた直感的なインターフェース。
- **Python 3.12+ 対応**: 最新のPython環境で動作し、研究用途でも扱いやすい構成。

## インストール
```bash
python -m venv .venv
source .venv/bin/activate  # Windowsの場合: .venv\Scripts\activate
pip install -r requirements.txt
```

### パッケージとして利用する場合
```bash
pip install .
```

## 使い方
1. `streamlit run app.py` を実行します。
2. ブラウザで表示されるUIから、テキストまたは画像を入力して解析結果（JSON）を確認します。
3. モジュールを直接使用する場合は `src/text_check.py` と `src/image_check.py` をインポートし、デモ関数 `_demo()` を実行して挙動を確認できます。

## テキスト検査アルゴリズム
- **TF-IDFコサイン類似度**: `sklearn.feature_extraction.text.TfidfVectorizer` を用いて、デフォルトでは1-2gramの単語ベクトルを生成します。`analyse_submission` の `ngram_range` パラメータを変更することで、文字ベースn-gram（例: `(2, 4)`）などに切り替えられ、日本語など空白を持たない言語にも対応可能です。
- **AIリピティションスコア**: 連続n-gramの出現回数を集計し、総n-gram数に対する重複n-gram数の割合を0.0〜1.0で返します。併せて、頻出n-gramの上位一覧（フレーズ、出現回数、割合）をJSONに含めることで、LLM生成文で見られがちな反復パターンを把握できます。`repetition_ngram_size` と `repetition_phrase_limit` を調整することで粒度を変えられます。
- **出力例**: `repeated_phrases` には `{ "phrase": "the quick", "count": 2, "share": 0.18 }` のような辞書が並び、分析結果の説明可能性を高めます。

## 画像検査アルゴリズム
- **pHash (perceptual hash)**: 画像をグレースケール化・リサイズし、DCT（離散コサイン変換）の低周波成分の中央値と比較してビット列を生成します。
- **類似度指標**: ハッシュ間のハミング距離をビット数で正規化し、0.0〜1.0でスコア化します。1.0に近いほど類似度が高いことを意味します。
- **耐性**: 軽微なリサイズや色調補正には強い一方、構図の大幅な変更やアフィン変換、敵対的ノイズには注意が必要です。

## 評価・ベンチマークのヒント
- テキスト解析は、既存の盗用事例・引用許容例・オリジナル例を含むサンプルセットで精度指標（Precision/Recall/F1）を測ると改善点が見つかります。
- 日本語テキストで高精度を求める場合は、MeCab/SudachiPyなどによる形態素解析を行った結果を `TfidfVectorizer` に渡す構成が推奨です。
- 画像検査では、pHashでは捕捉しづらい変形（回転、大幅なクロップ）に対して、畳み込みニューラルネットワークやCLIPの特徴量ベクトルとのハイブリッド構成が今後の拡張案として有効です。

## テスト
純粋なPython環境でも動作するよう、主要モジュールを対象としたユニットテストを用意しています。

```bash
python -m unittest discover
```

`tests/test_text_check.py` と `tests/test_image_check.py` では、テキスト類似度・リピティション解析とpHash類似度計算が想定通りに機能することを確認しています。

## ライセンス
本プロジェクトは [MIT License](LICENSE) の下で提供されます。

> **補足:** `LICENSE` ファイルはMITライセンスの**定型文そのもの**です。最初の著作権表記のみプロジェクト名に置き換えていますが、それ以外の文章は一般的なMITライセンスと同一です。プロジェクトの制作年を反映したい場合は、冒頭の年号を任意のものに変更してください。READMEはソフトウェアの仕様・使い方を解説する文書であり、ライセンス文は法的条件を示す別文書である点にご注意ください。

## 開発・貢献
バグ報告や改善案があればIssueやPull Requestでお知らせください。ツールの活用事例や検証結果も歓迎しています。
