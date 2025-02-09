+++
title = "dd と ddrescueについて"
[extra]
genre = "Linux"
+++

ddとddrescueは似て非なるものであるので個別にメモ書き

## dd
```
sudo dd if=<input file> of=/dev/<device> status=progress
```
- bs=512がデフォルトなので bs=4Mくらいにすると良いらしい

## ddrescue
主に[ここ](https://wiki.archlinux.jp/index.php/ディスクのクローン)
```
ddrescue --force -d -r3 -n /dev/sdX(partition to be recovered) /dev/sdY(partition where date is written) rescue.map
```
がだめなときはPartitionごとにrescueすればよい
```
ddrescue --force -d -r3 -n /dev/sdX1 /dev/sdY1 rescue.map
```
