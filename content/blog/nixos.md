+++
title = "NixOSをVirtualBoxにインストールする"
date = 2019-04-01
updated = 2025-02-03
+++

ツイッターで時々耳にしていたNixOSをVirtualBoxにインストールします。今回はminimal installerを使います。目標は私が思う最低限のインストール、即ち一般ユーザからログインしてsudoを使える状態にします。

VirtualBoxは使える前提とし、EFIブートでの環境を構築します。

なお英語のつづりに自信がないのでコマンドやパスのつづりが間違っている可能性があります。シェルのタブ補完を有効活用しましょう。

### インストーラの取得

[Getting NixOS](https://nixos.org/nixos/download.html) ダウンロードページ

なお "VirtualBox appliances" と書かれた仮想化に適した（？）インストーラもありますが、そちらはX11とKDE Plasma5が入っているバージョンしかなく、その分サイズが大きくなります。今回、GUIは必要ないので通常インストール用isoの "Minimal installation CD, 64-bit Intel/AMD" をダウンロードします（この記事では nixos-minimal-18.09.2436.395a543f360-x86_64-linux.iso を使っておりサイズは530MBでした、小さいですね）。

インストール方法が変わっていたり、パッケージが存在しなかったりします。公式マニュアルの [NixOS manual](https://nixos.org/nixos/manual/) （英語）を適宜参照してください。

### VirtualBoxの設定

EFIの時代はもう来ちゃってるんだよね…

そもそもなぜVirtualBoxを使うのかといえば実機インストールの練習のためなので環境も実機に合わせていかなければなりません。ならば最近のPCに合わせてUEFIを使いましょう、というのは自然な流れです…だと思います。ということでVirtualBoxをEFIブートにします。

まず、 [NixOS manual #2.5.3 Installing in a VirtualBox guest](https://nixos.org/nixos/manual/index.html#sec-instaling-virtualbox-guest) を参照しながらメモリ、ディスク容量などを決めます（私はメモリ4096MB、HDD可変16GBに設定しました）。

次に、設定→システムのマザーボードタブを選び「EFIを有効化」にチェックします。これでEFIで起動します。なおこの設定をしないとBIOSでブートしてしまいUEFIブートローダのインストールが困難になるので忘れないようにしましょう。

また、設定→システムのプロセッサータブから「PAE/NXを有効化」にチェック、設定→システムのアクセラレーションタブから「VT-x/AMD-Vを有効化」にチェックします。参考 : [NixOS manual](https://nixos.org/nixos/manual/index.html#sec-instaling-virtualbox-guest)

最後にダウンロードしたisoイメージをストレージのIDEコントローラに入れて設定は完了です。

### 起動

なぜこんな見出しを付けたのかと言うと、VirtualBoxではnomodesetで起動しないと途中で画面がフリーズするからです。

起動するとモード選択の画面が出ます。10秒で自動起動してしまうので↓キーを押します。そうすると"NixOS ... Installer (nomodeset)"が選択されます。エンターキーを押します。無事rootでログインできるかと思います。auto loginなのでパスワードは要りません。

もし普通に起動しても問題ないならそれでいいです。

### インストール

日本語キーボードなら`loadkeys`で日本語キーボードをロードします:

```
# loadkeys jp106
```

またネットワーク接続を確認します:

```
# ip a  
# ping 1.1.1.1
```

もし接続がうまく言ってないのであれば [ネットワーク設定 - ArchWiki](https://wiki.archlinux.jp/index.php/%E3%83%8D%E3%83%83%E3%83%88%E3%83%AF%E3%83%BC%E3%82%AF%E8%A8%AD%E5%AE%9A) などを見てください。Archと同じくNixOSは`systemctl`が使えます。

#### パーティショニング

EFIブートなのでパーティションテーブルはGPTを使います。私は`gdisk`のほうがGUIDコード`の選択などがわかりやすいと思っているので`gdiskでパーティションを切ります。[Arch Linuxインストール （OSインストール編）| UEFI, GPT, XFSを使用してインストール | 普段使いのArch Linux](https://www.archlinux.site/2016/03/arch-linux-uefi-gpt-xfs.html) を参考にしました。ワンライナーがお好みの方は公式マニュアルのように`parted`を使います。

今回はシンプルにルートパーティションとブートパーティションのみを作ります。最近のPCはメモリ容量が大きいのでハイバネーションをしないかぎりスワップはいらないのではないかと思います。実際、自動インストールしたLinuxMintを使っていた頃、システムモニタを見てもスワップが使われていたときを見たことがありません。もっとも私は詳しくないのでこんな場合に必要だ、というのを知っている方はコメントください。

閑話休題。`lsblk`でディスクを確認します:

```
# lsblk  
sda     8:0    0    16G  0 disk
```

HDDを16GBに設`定したのでこう書かれていました。この場合/dev/sdaを設定することになります。`gdiskでパーティションを切ります。まずはパーティションテーブルを作ります:


```# gdisk /dev/sda  
Command (? for help):o
This option ...  
Proceed? (Y/N):y
```

次にパーティションを切ります。16GBのうち256MBをブートパーティションに割り当て、残りをルートパーティションに割り当てます:


```Command (? for help):n
Partition number (...) :  
First sector (...) :  
Last sector (...) : +256M
Hex code or GUID (...) : ef00
  
Command (? for help):n
Partition number (...) :  
First sector (...) :  
Last sector (...) :  
Hex code or GUID (...) :
```

`:`の後に何も書いていない箇所は何も書かなくていいです。最後に切られたパーティションをディスクに書き込みます:


```Command (? for help):w
Final check complete. About...  
Do you want to proceed?(Y/N):y
OK; writing...  
The operation has completed successfully.
```

これでパーティションが切られました。`lsblk`で確認します:


```# lsblk  
sda      8:0    0     16G  0 disk  
├sda1   8:1    0    256M  0 part  
└sda2   8:2    0   15.8G  0 part
```

パーティションが2つできました。

#### フォーマット

パーティションのフォーマットをします。ブートはexFAT（EFIはこれでないといけない）、ルートはお好みのフォーマッタでフォーマットします。私はいつも何も考えずext4を選択しています:


```
# mkfs.fat -F 32 /dev/sda1  
# mkfs.ext4 /dev/sda2
```

フォーマットされました。

#### マウント

sda2がルート、sda1がブートであることに注意してマウントします:


```
# mount /dev/sda2 /mnt  
# mkdir /mnt/boot  
# mount /dev/sda1 /mnt/boot  
# lsblk  
sda      8:0    0     16G  0 disk  
├sda1   8:1    0    256M  0 part /mnt/boot  
└sda2   8:2    0   15.8G  0 part /mnt
```

マウントされました。

#### システムのインストール

NixOSの肝であるconfiguration.nixを生成します:


```
# nixos-generate-config --root /mnt
```

生成されました。パスは /mnt/etc/nixos/configuration.nix です。ここで公式マニュアルは

"If you have network access, you can also install other editors — for instance, you can install Emacs by running `nix-env -i emacs`"

とも言っていますが、ここでインストールされるエディタはシステムにインストールされない、即ち一時的なものであるのでVim,Emacsその他CUIエディタでないと嫌だ、またはnanoが嫌いという人以外はインストーラ付属のnanoを使えばいいと思います。

そして何を編集するのかというと、EFIの場合生成されたconfiguration.nix内のパラメータ、`boot.loader.systemd-boot.enable` の値です。これはデフォルトで`true`になっているはずで、そのままでいいです:


```
# grep systemd-boot /mnt/etc/nixos/configuration.nix  
  boot.loader.systemd-boot.enable = true;
```

しかし日本語キーボードユーザはキーボード設定をjp106キーボードにしなければならないのでその設定を書き込みます。#でコメントアウトされている行に`i18n = ...`から始まるブロックがテンプレートとして書いてあるので先頭の#を消してKeyMapを`us`から`jp106`に直します:


```
i18n = {  
  consoleFont = "Lat2-Terminus16";  
  consoleKeyMap = "jp106";  
  defaultLocale = "en_US.UTF-8";  
}
```

このとき`defaultLocale`は変えません。インストール後に文字化けを起こすからです。ロケールは日本語フォントを入れてから変えます。

またVirtualBoxを使っている人は適当な行に以下を追加します:


```
boot.kernelParams = ["nomodeset"];
```

これは起動でみたnomodesetです。そう、NixOSはカーネルパラメータも含めシステム全体をすべてこのconfiguration.nixファイルで扱います。一括で扱えるのでとても楽そうです。しかしFile Hierarchy Standard(FHS)には準拠していません（[NixOS - Wikipedia 3 #Implementation](https://en.wikipedia.org/wiki/NixOS#Implementation)）。

これらを書き込んだらシステムのインストールです:


```
# nixos-install
```

最小限のシステムなので比較的早く終わるはずです。最後にrootのパスワードの設定が促されるのでrootパスワードを設定します。終わったら再起動します:


```
# reboot
```

すると今度はインストールディスクと打って変わって地味なシンプルなsystemd-bootのブートローダが起動します。エンターキーを押すか5秒間だけ待ってやると起動します。ログイン画面（と言っても黒いままであるが）になったら、rootとして入ります（インストールディスクが入ったままなので、もしそちら（起動時に豪華な画面が出る方）が起動してしまったら一番下のshutdownを選択し光学ディスクドライブを空にします）。

#### エディタのインストール

Vimをインストールしましょう…と矯正するのはいいけど強制するのは良くないってばあちゃんが言ってたのでVimかEmacs、または他のCUIエディタをインストールします。nanoで十分だというひとはインストールしなくていいです。パッケージのインストールのコマンドは以下です（ここではVimをインストールする）:

```
# nix-env -i vim
```

Vimがインストールされました。以降テキストの編集ではVimを使います。

#### 一般ユーザの追加

常にルートでログインするのは良くないとされているので一般ユーザを追加します。先程「NixOSはカーネルパラメータも含めシステム全体をすべてこのconfiguration.nixファイルで扱います」と言いました。だから一般ユーザの追加も`useradd`ではなく直接configuration.nixに書き込んでみたいと思います。

configuration.nixにはコメントアウトされたテンプレートとして`users.users.guest=`から始まるブロックがあるので、コメントアウトを外し以下を書き込みます。


```
# vim/etc/nixos/configuration.nix  
  users.users._name_ = {  
      shell = pkgs.bash;
      createHome = true;
      home = "/home/_name_";
      extraGroups = ["wheel"];
      isNormalUser = true;  
      uid = 1000;  
  }
```

`_name_`には一般ユーザのユーザ名を入れてください。上から順番に説明します。

##### `shell = pkgs.bash;`

ユーザのデフォルトシェルをbashにします。zshやfishなど他のシェルをインストールし、デフォルトシェルをいずれかに変更する場合は{ }外に
```
programs._**sh_.enable = true;
```

を、{ } 内に
```
shell = pkgs._**sh_;
```

を書きます。すべてのユーザのデフォルトシェルを設定するには{ } 外に
```
users.defaultUserShell = pkgs._**sh_;
```

を書きます。

##### `createHome = true;`

ユーザにホームディレクトリをあたえるかどうか設定します。これはすべてのユーザ一括で指定する束縛変数がないようです（あったら教えてください）。

##### `home = "/home/_name_";`

ユーザのホームディレクトリを設定します。ユーザ名とディレクトリ名は違っていてもコンパイルが成功し、ログインもできます。が、同じ名前のほうが無難でしょう。

##### `extraGroups = ["wheel"];`

ユーザの入るグループを設定します。`useradd`の`-G`に当たる部分でしょうか。複数のグループが設定できるようにextraGroupsはリストになっています。リストはスペースで区切ります。Nix言語の仕様ではリスト内の型が違ってもいいようですがextraGroupsの型はlist of stringsです。

参考

    [Nix Expression Language - NixOS Wiki #Types](https://nixos.wiki/wiki/Nix_Expression_Language#Types) 言語仕様について

    [nixpkgs/users-groups.nix at release-18.09 · NixOS/nixpkgs · GitHub](https://github.com/NixOS/nixpkgs/blob/release-18.09/nixos/modules/config/users-groups.nix) extraGroupsについて

これらを書き込んだら以下を実行します:
```
# nixos-rebuild switch
# passwd _name_
```

`passwd _name_` で一般ユーザのパスワードを設定します。

さて、重要なのは前者`nixos-rebuild switch`。このコマンドをすると何が変わるでしょうか。再起動してみます（インストールディスクが入ったままなので、もしそちら（起動時に豪華な画面が出る方）が起動してしまったら一番下のshutdownを選択し光学ディスクドライブを空にします）。

再起動すると

```
NixOS (Generation 1 NixOS ...
NixOS (Generation 2 NixOS ...
```

と２つあることがわかります。エンターキー押下または5秒間だけ待ってやるとGeneration2が起動します。これは`nixos-rebuild switch`でシステムが更新され、また前のシステムは残っていることを意味します。一般ユーザでログインし、ブートローダの設定を覗いてみます:


```
$ ls /boot/loader/entries/
nixos-generation-1.conf nixos-generation-2.conf
```

2つあります。結局ここから選んでいたということです。`diff`ってみます。

```
$ cd /boot/loader/entries/
$ diff nixos-generation-1.conf nixos-generation-2.conf
...
5c5
< options ... init=/.../d9iv1...  
---
> options ... init=/.../7sijy...
```

（文字列は自分のを適当に拾ってきましたorz）

initが指すファイルが別物です。全く違うシステムを起動しているのと同じです。故に新しい世代で故障しても古い世代に戻れば無傷のままいられるということです（もちろんこれは依存関係が壊れたなどの故障であり、HDDが物理的にぶっ壊れた場合は…手厚く葬ってあげてください）。

試しに再起動して古いシステムで起動します。一般ユーザでログインしようとしてもできないことがわかります。なぜならこの世代の時まだ一般ユーザを作っていない、即ちconfiguration.nixが適用されていないからです。/etc/passwdを見ても_name_ ユーザはいません。

このようにNixOSでは`nixos-rebuild switch`で古いシステムを残しながら更新していきます。それが一番のポイントです。

私はまだNixOSをあまり使っていませんが、このコマンドはおそらくよく使うコマンドになるでしょう。

参考

    [NixOS - NixOS Wiki #Generations](https://nixos.wiki/wiki/NixOS#Generations) 世代について

    [NixOS は良いぞ！という話 - カラクリスタ・ノート](https://scrapbox.io/kalaclista/NixOS_%E3%81%AF%E8%89%AF%E3%81%84%E3%81%9E%EF%BC%81%E3%81%A8%E3%81%84%E3%81%86%E8%A9%B1) 200世代以上更新している方

### ルート取れるの？

忘れていました、一般ユーザで`sudo`を試しましょう。コマンドはなんでもいいです。

```
$ sudo pwd
  
We trust you have received the usual lecture from the local system  
Administrator. It usually boils down to these three things:  
  
    #1) Respect the privacy of others.  
    #2) Think before you type.  
    #3) With great power comes great responsibility.  
  
sudo password for _name_:  
/home/_name_
```

お疲れ様でした。