+++
title = "EXIFから露光を表示するアプリケーションを作った"
date = 2025-03-13
+++

完成したものは[こちら](../../exif-analyzer)

elm でできている。
exif を解析する部分は exif-js を使っているので，elm と JS を port で繋いでいる。

## ハマったポイント
javascript Object は javascript では JSON として Parse 可能だが，
port にそのまま送ると，Number Object が elm では Decode 不可能なので，
JSON.stringify を使い， `port getExif : (String -> msg) -> Sub msg` としている。