+++
title = "open webui で model をpull できなかった"
extra.genre = "Docker"
+++

## 事象
windows11 上の WSL ubuntu 24.04.3 の docker で openwebui を動かしており，
それをUpdateしたかったので[公式](https://docs.openwebui.com/getting-started/updating/)どおりupdateし
`docker run -d -p 3000:8080 -v open-webui:/app/backend/data --name open-webui ghcr.io/open-webui/open-webui:main`
でrunしたが，過去に使っていたLLMモデルが表示されず，新しく ollama.com から pull することもできなかった（その項目が表示されなかった）．

## 解決方法
この[記事](https://qiita.com/taro_yamada_dewanokami/items/19326b535c3f40482696)にかかれているようにOllama 専用イメージ open-webui:ollama を動かすことで解決．

update 手順は以下．

```bash
sudo docker stop open-webui
sudo docker rm -f open-webui
sudo docker pull ghcr.io/open-webui/open-webui:main
sudo docker run -d -p 3000:8080 --gpus=all -v ollama:/root/.ollama -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:ollama
```

## 補足
もしかしたら最初に導入したときにその記事を参照したからかもしれない．

## なぜ動くのかChatGPTが説明してくれた

なるほど、やっと動いたのですね！🎉
では今回の違いを整理して、なぜこのコマンドで成功したかを解説します。

---

## 1. 違いのポイント

あなたが動かしたコマンド：

```bash
docker run -d -p 3000:8080 --gpus=all \
  -v ollama:/root/.ollama \
  -v open-webui:/app/backend/data \
  --name open-webui \
  --restart always \
  ghcr.io/open-webui/open-webui:ollama
```

以前の失敗したコマンドとの違いは大きく分けて3つあります：

---

### 🔹 ① イメージの違い

* 以前：`ghcr.io/open-webui/open-webui:main`
* 今回：`ghcr.io/open-webui/open-webui:ollama`

**違い**：

* `main` → ベースの Open WebUI イメージ、Ollama 連携はオプション
* `ollama` → Ollama 専用統合ビルド済み

  * Ollama API に接続するための依存ライブラリや設定が初めから含まれている
  * Docker コンテナ内で Ollama 接続用の内部処理が組み込まれている

→ つまり **Ollama 専用のイメージを使うことで、接続設定やネットワーク問題を回避できるようになっている**

---

### 🔹 ② ボリュームマウントの違い

* Ollama のデータディレクトリを `/root/.ollama` にマウントしています：

  ```bash
  -v ollama:/root/.ollama
  ```
* これにより **コンテナ内部で Ollama のモデル情報や設定を正しく認識**できる
* 以前のコマンドは Ollama データをマウントしていなかったため、コンテナ内部から Ollama モデルにアクセスできなかった

---

### 🔹 ③ GPU オプション

* `--gpus=all`
* Ollama やモデル推論に GPU を使う場合の設定
* 今回は GPU がある環境なので、推論も問題なく動作

> これは接続自体とは直接関係ありませんが、推論性能のために重要です

---

## 2. なぜ今回動いたのか

* Ollama 専用イメージ `open-webui:ollama` は **内部で Ollama 接続が組み込まれており、WSL 内 Docker でもホストIP問題を意識せず動作**
* Ollama のデータディレクトリをマウントしているので、コンテナ内からモデルが直接参照可能
* そのため、以前のような「Network Problem」は発生しなかった

---

### まとめると

| 項目          | 以前のコマンド           | 今回のコマンド                         |
| ----------- | ----------------- | ------------------------------- |
| Docker イメージ | `open-webui:main` | `open-webui:ollama`（Ollama 統合済） |
| Ollama データ  | マウントなし            | `/root/.ollama` をマウント           |
| API 接続      | 手動設定必要            | 内部で自動接続                         |
| GPU         | なし                | `--gpus=all`                    |
| 結果          | Network Problem   | 正常に接続＆動作                        |

---

💡 **結論**
今回動いたのは **「Ollama 専用イメージ + Ollama データのボリュームマウント」** のおかげです。

* 以前の main イメージでは、WSL + Docker の環境でホストの Ollama にアクセスするのが難しかった
* 専用イメージを使うことで、コンテナ内部から Ollama に直接アクセスできるようになった

---
