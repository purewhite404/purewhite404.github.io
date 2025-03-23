+++
title = "文書をGnuPGで暗号化する"
[extra]
genre = "security"
+++

公開鍵暗号を使って簡単なメッセージの送受信を行う。

注意点は
- メッセージを受け取る側が鍵を生成する
- 受け取る側は秘密鍵を漏洩してはならない

## 方法
ターミナルにて(WindowsならWSL, あるいはGnuPGをインストール)
1. 鍵生成（メッセージを受け取る側）
```bash
gpg --full-gen-key
gpg --output public.key --armor --export {mail address}
```
生成された `public.key` と `{mail address}` を何らかの方法で送る

2. 暗号（メッセージを送信する側）
`public.key` と `{mail address}`を受け取った後
```bash
gpg --import public.key
echo "<message you want to send>" | gpg --encrypt --armor -r {mail address} > encrypt.txt
```
によってメッセージを暗号化し、`encrypt.txt` を送信する。

3. 復号（メッセージを受け取った側）
`encrypt.txt` を受けとった後
```bash
gpg --decrypt encrypt.txt
```