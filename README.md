# StudyLog — 学習記録・目標管理 Web アプリ

![test](https://github.com/esfine80jp/studylog/actions/workflows/test.yml/badge.svg)

## 概要

日々の学習を記録し、科目別の進捗をグラフで確認できる Web アプリです。
Flask と SQLite で作られています。

newer commit

## デモ

アプリ URL: 準備中

テスト用アカウント: demo@example.com / パスワード: demo1234
## 機能

- メールアドレスとパスワードによるユーザー認証
- 学習記録の追加・編集・削除（科目・日付・学習時間・メモ）
- 今週の学習時間の集計とグラフ表示
- 科目別の週間目標設定

## 技術スタック

| 項目 | 使用技術 |
|:--|:--|
| Web フレームワーク | Flask 3.0 |
| データベース | SQLite |
| 認証 | Flask-Login + Werkzeug |
| グラフ | matplotlib + japanize-matplotlib |
| フロントエンド | Bootstrap 5 |
| デプロイ | Render |
| 開発環境 | Google Colaboratory |
## ローカルでの実行方法

```bash
git clone https://github.com/ユーザー名/studylog.git
cd studylog
pip install -r requirements.txt
python app.py
```

## 作者

[GitHub プロフィールへのリンク]
