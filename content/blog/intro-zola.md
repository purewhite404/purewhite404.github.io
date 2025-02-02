+++
title = "ホームページに Zola を導入した"
date = 2025-01-23
updated = 2025-01-31
+++

ホームページに Jamstack の一つである [Zola](getzola.org) を導入した。

## Attaching theme
- theme には [Hook](https://github.com/InputUsername/zola-hook) を用いた。
    - `config.toml` に theme を設定し、`content/` と `content/blog` にそれぞれ `_index.md` を置けば動く。

## Deploy using [shalzz/zola-deploy-action](https://github.com/shalzz/zola-deploy-action)
- Custom Domain を設定する場合は `static/CNAME` ファイルに使用したいドメインを書く
