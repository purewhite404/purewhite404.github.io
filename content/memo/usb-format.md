+++
title = "USBメモリがオシロスコープで認識されない場合は，Linuxでフォーマットすると良い"
extra.genre = "Windows"
+++

windows でフォーマットした USB メモリが keysight のオシロスコープで認識されなかった．
ちなみにMacもだめだった．
そのため，Virtual Box 上の Kali linux で
`gdisk` 等でGPTのパーティションを切った後，`mkfs.fat -F 32 /dev/sdX -I` で fat32 フォーマットしたところ
USB メモリを認識した．
