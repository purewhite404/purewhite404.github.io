+++
title = "Hermes agent on alpine linux で claude model を使用時に web search すると segmentation fault するバグ"
extra.genre = "Linux"
+++

hermes agent cliを用いて検索をしたときの事象。
`mcp__web_search`が表示された直後に segmentation fault を吐いて落ちる。
`hermes --tui`のときは落ちはしないが、エラーをずっと繰り返す挙動をしていた。
今回は jiter 0.13 の musl に対するバグがあるためだった。
以下で修正できるそう。updateされたら破壊されるかも

```sh
# Alpine
sudo apk add --no-cache uv

# Hermesの実際のvenvに入れる
uv pip install --python ~/.hermes/hermes-agent/venv/bin/python 'jiter>=0.14,<1'

# 確認
~/.hermes/hermes-agent/venv/bin/python -c \
'import importlib.metadata as m; print(m.version("jiter"))'
```

「Hermesの更新・再インストールで古いlockfileが復元される場合は、上記を再実行してください。」とのこと。
