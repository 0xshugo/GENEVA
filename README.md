# GENEVA – Generative Ethics Validator

GENEVA（Generative Ethics Validator）は、生成コンテンツの倫理面をサポートするためのテキストおよび画像類似度チェッカーです。AIによる繰り返しの検出や、画像のpHash比較など、教育・研究・クリエイティブ制作のワークフローを支援します。

## 特徴
- **テキスト検査**: TF-IDFコサイン類似度を用いた文章比較と、AIリピティションスコアによる繰り返し判定。
- **画像検査**: 離散コサイン変換（DCT）を利用したpHash類似度計算で、視覚的に近い画像を抽出。
- **Streamlit UI**: 「Text Check」「Image Check」のタブを備えた直感的なインターフェース。
- **Python 3.12+ 対応**: 最新のPython環境で動作し、研究用途でも扱いやすい構成。

## インストール
```bash
python -m venv .venv
source .venv/bin/activate  # Windowsの場合: .venv\\Scripts\\activate
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

## ライセンス
このプロジェクトは [MIT License](LICENSE) の下で提供されます。
