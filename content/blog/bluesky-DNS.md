+++
title = "Bluesky のアカウント名をjr2hao.devに設定した"
date = 2025-02-02
+++

[Bluesky/ATProtocol の日本コミュニティー](https://bluesky-jp.github.io/welcome-bluesky/docs/walks/custom_domain/setting/use_dns_record)の記事を参考にして DNS レコードを設定した。
bluesky から与えられる DID Placeholder を DNS 設定のTXTレコードに記入するだけ

| Type | Name     | TTL  | Content         |
| ---- | ----     | ---  | -------         |
| TXT  | _atproto | auto | did=did:plc:*** |
