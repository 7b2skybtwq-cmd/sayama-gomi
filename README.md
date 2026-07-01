# Sayama Gomi for Quote/0

狭山市「入間川2丁目・富士見1・2丁目」向けの、Quote/0表示用PNGを毎日自動生成するテンプレートです。

> [!IMPORTANT]
> 現在の `data/schedule-2026.json` は6日分だけのサンプルです。公開前に狭山市公式カレンダーを見ながら、2026年分を追記してください。未登録日は「収集なし」と表示されます。

## 使い方

1. GitHubで `sayama-gomi` という公開リポジトリを作成
2. このフォルダの中身をそのままアップロード
3. GitHub Pagesを有効化
   - Settings → Pages
   - Source: `Deploy from a branch`
   - Branch: `main` / `/root`
4. Actionsを有効化
5. Quote/0に以下のURLを登録

```text
https://あなたのGitHub名.github.io/sayama-gomi/index.png
```

## 年1回の更新

`data/schedule-2026.json` をコピーして `schedule-2027.json` を作り、公式カレンダーに沿って日付とごみ種別を書き換えます。

```json
"2027-04-01": "もやすごみ"
```

使用できるごみ種別：

- もやすごみ
- びん・缶
- ペットボトル
- プラスチック
- 古紙・古布
- もやさないごみ
- 収集なし

## ローカル確認

```bash
pip install -r requirements.txt
python generate.py --date 2026-07-01
```
