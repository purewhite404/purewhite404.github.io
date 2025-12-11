+++
title = "ホームページに Zola を導入した"
date = 2025-01-23
updated = 2025-12-11
+++

ホームページに Jamstack の一つである [Zola](getzola.org) を導入した．

## Attaching theme
- theme には [Hook](https://github.com/InputUsername/zola-hook) を用いた．
    - `config.toml` に theme を設定し，`content/` と `content/blog` にそれぞれ `_index.md` を置けば動く．

## Deploy using [shalzz/zola-deploy-action](https://github.com/shalzz/zola-deploy-action)
- Custom Domain を設定する場合は `static/CNAME` ファイルに使用したいドメインを書く

### how to deploy key update
1. Deploy key の有効期限が切れたときは [tokens](https://github.com/settings/tokens) にアクセスして鍵をアップデート．
    - Generate New Token(classic) から `public_repo` にチェックをつけてTokenを生成する．
1. 生成された token をコピーする（このタブを消すともう一度見ることはできない）
1. 自分のリポジトリの settings/secrets/actions から GITHUB_TOKEN を編集
