+++
title = "Diver OSINT CTF 2025 WriteUp"
date = 2025-06-08
+++

Diver OSINT CTF 2025にチーム`assemb1ytea`として参加したので，解いた問題についてWriteUpを書きます．
ちなみに `assemb1ytea := leet(assembly + センブリ茶)` です．

## Advertisement | <sub>introduction</sub>

ロシアの兵士募集広告の位置を当てる問題．

広告の下の`TOKIO-CITY`についてOCRをかけて`рестораны ТОКИО-СIТY`を得る．これをgoogle mapで検索．
モスクワには該当する雰囲気のTOKIO-CITYは無いので，もう少し範囲を大きくするとサンクトペテルブルクにもあることがわかる．
サンクトペテルブルクで絞って拡大しこのエリアを検索すると，数件～十数件見つかるので全探索すると
[この店](https://maps.app.goo.gl/DH5Bv6SnmUGiYeYy6)がヒットする．
Street Viewで動いて正確な撮影場所を割り出すと[59°56'34.5"N 30°16'43.4"E](https://maps.app.goo.gl/LdgKzTYRLFWDCiFm9)

"рестораны ТОКИО-СIТY" を検索すると全部は出てこないのでGoogle mapを拡大し，「このエリアを検索」するのが良い．



## hole | <sub>geo, medium</sub>

地面に空いた穴の場所を当てる問題．

与えられた画像をgoogle imageにかけると車の宣伝の記事がヒットし，その中のyoutubeを見ると山西省大同市の飛行場で行われていそうなことがわかる．
あとは山西省大同市の飛行場をひたすら探した．
[39°24'20.1"N 114°09'50.7"E](https://maps.app.goo.gl/nsJrg2DioVoWtAKaA)

ただ，結局これが飛行場なのかどうかはよくわからない．"机场"，"跑道"などで検索したがヒットしなかった．工夫が必要．


## platform | <sub>geo, easy</sub>

撮影場所の駅がどこか当てる問題．

鉄道には詳しくないので本当は違うのかもしれないが，
乗車口の表示から，オレンジ色で12両が止まるのでJR中央線であると決めつけ，
また6両も止まることから，立川以西であるだろうと予測．
その付近を拡大して"らいと"を検索すると牛浜駅であることがわかる．



## night_street | <sub>geo, hard</sub>

夜に撮影された手ブレの写真の位置を当てる問題．

リンガーハットが特徴的な形なので長崎の本店だろうと思ったが他にもあるらしいことがわかったので方針を変える．
コンクリート舗装の道路が特徴的なので"コンクリート舗装 国道"で調べると[このPDF](https://www.nup.or.jp/nui/user/media/document/investigation/h29/No134.pdf)
が出てくる．
なぜかわからないが，名古屋にあるだろうと**エスパー**し，名古屋のリンガーハットをgoogle mapで検索すると十数件出てくるので，全探索すると弥富通店が合致するので
弥富通クリニックが答え．たしかにこの通りは前述PDFの4ページに赤く塗りつぶされたコンクリート舗装区間であることがわかる．しかし県道だった．

なぜ名古屋？→わからない，勘．



## Talentopolis | <sub>geo, medium</sub>

記事内の写真の場所を当てる問題．一番解きごたえがあり，良問と感じた．

---
注意として，与えられたリンクを踏んでも最初はなぞのスライドショーを見せられるのでリロードしなければならない←Hard!

---

記事はOficina de Información y Prensa de Guinea Ecuatorialが書いており，記事内に`malabo`ともあるので赤道ギニアのマラボで開催されていることがわかる．
また，San juan地区はgoogle mapに聞いてもわからないので，`San juan de malabo`で検索すると，
`Afri Mall`という施設が最近オープンした記事を見つけた．[Afri Mall](https://maps.app.goo.gl/J7fZuK92utJdTTJx9)
があり，近くに"unicasa San juan"もあるのでこのあたりがSan juan地区であることがわかる．

また，"talentopolis san juan de malabo" で検索すると，[4枚の写真を持つ記事](https://ahoraeg.com/cultura/2024/09/10/inicia-el-proyecto-talentopolis-en-el-barrio-san-juan-de-esta-ciudad-capital/)
がヒットする．
また，"san juan de malabo" で検索すると[VIVIENDAS SOCIALES DE SAN JUAN MALABO - Youtube](https://www.youtube.com/watch?v=YVkiYkFndPE)
も見つかり，この動画の公営住宅の壁と4枚の写真を持つ記事の壁や柱が似ていることから"VIVIENDAS SOCIALES DE SAN JUAN MALABO"
をGoogle mapで検索すると，これらがAfri mallの隣にあることがわかる．

4枚の写真を持つ記事を見ると，ステージの左にも棟があり，風船遊具の奥は道路ではなく民家があることから
航空写真と照らし合わせて，[3°44'15.2"N 8°47'47.5"E](https://maps.app.goo.gl/VqL6YUb5U3wVriJz7)が答えとなる．
この答えは一発ではなかなかわからないと思うので，何度かAttemptするのが良い．



## radar | <sub>military, medium</sub>

与えられた写真に映るレーダー施設を保有・管理する中国人民解放軍(PLA)の部隊及び分隊番号を答える問題．

チームメンバーが福建省海岸を全探索して位置を特定したので，緯度経度はわかっていた．

結論から言うと3回目の試行で
PLA unit 95980 52nd でDuckduckgo検索したら出てきた記事，
[Chinese Armed Forces ORBAT Part 7: Radars and SAMs](https://jjamwal.in/yayavar/chinese-armed-forces-orbat-part-7-radars-and-sams/)
Over Horizon    Xiasha Village, Changle    92985    Receiving station    25°47’50.39″N    119°36’43.67″E    Unit 84, Naval 1st Brigade
より，92985部隊 84thが答え．しかし，この記事が信頼できるソースであるかはよくわからない．

[この記事](https://www.globalsecurity.org/wmd/world/china/oth-swr.htm)からは95980部隊が運用しているように思えるが，よくわからない．4回の試行を要した．



## what3slashes | <sub>geo, medium</sub>

画像の撮影された位置での建築工事の時期を答える問題．

ハガキをgoogle imageにかけるとCNNの記事がヒットし，what3wordsという3単語で位置を特定するサービスを使って郵便を届けているモンゴルであることがわかる．
チームメンバがChatGPTでOCRさせ`бумба.цогц.бататгав`と書かれていることがわかる．ここで下手にキリル文字の筆記体から自力で推測するのは若干字形が違うのでやめたほうがいい．
これをwhat3wordsで調べると緯度経度がわかる．
Google Earth Proをインストールして，時間巻き戻しを使うことで，この位置での建築工事が2018/10に行われたことがわかる．Google Earth Proを使うのもChatGPTのアイデア．