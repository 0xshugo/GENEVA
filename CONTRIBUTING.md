# Contributing to GENEVA

GENEVAプロジェクトへの貢献を検討いただき、ありがとうございます！

## 開発環境のセットアップ

```bash
# リポジトリをクローン
git clone https://github.com/YOUR_USERNAME/GENEVA.git
cd GENEVA

# 仮想環境を作成
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 依存関係をインストール
pip install -r requirements.txt

# テストを実行して環境を確認
python -m unittest discover
```

## コードの品質基準

### テスト
- 新機能には必ずテストケースを追加してください
- すべてのテストが成功することを確認してください: `python -m unittest discover`
- エッジケースもカバーしてください

### コードスタイル
- PEP 8に準拠してください
- 型ヒントを使用してください
- 関数には適切なdocstringを付けてください

### コミットメッセージ
明確で簡潔なコミットメッセージを書いてください：

```
feat: Add Japanese text tokenization support
fix: Resolve merge conflict in image_check.py
docs: Update README with installation instructions
test: Add edge case tests for empty input
```

プレフィックス：
- `feat:` - 新機能
- `fix:` - バグ修正
- `docs:` - ドキュメントのみの変更
- `test:` - テストの追加や修正
- `refactor:` - リファクタリング
- `perf:` - パフォーマンス改善

## Pull Requestのワークフロー

1. **Forkとブランチ作成**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **変更を実装**
   - コードを書く
   - テストを追加
   - ドキュメントを更新

3. **テスト実行**
   ```bash
   python -m unittest discover
   ```

4. **コミット**
   ```bash
   git add .
   git commit -m "feat: Your feature description"
   ```

5. **Push**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Pull Request作成**
   - GitHubでPull Requestを作成
   - 変更内容を明確に説明
   - 関連するIssueがあればリンク

## バグ報告

バグを発見した場合は、Issueを作成してください。以下の情報を含めると助かります：

- バグの説明
- 再現手順
- 期待される動作
- 実際の動作
- 環境情報（OS、Pythonバージョン）
- エラーメッセージやスタックトレース

## 機能リクエスト

新機能のアイデアがある場合：

1. まずIssueで議論を開始してください
2. ユースケースを説明してください
3. 実装案があれば共有してください

## 質問・サポート

質問がある場合は、Issueを作成するか、既存のIssueを検索してください。

## ライセンス

貢献したコードはプロジェクトのライセンス（MIT License）の下で公開されます。
