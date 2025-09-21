+++
title = "Matlab のグラフプロットでフォント指定"
extra.genre = "Matlab"
+++

matlab のplotでフォントをLatexにしたいとき
```matlab
xlabel("hoge", Interpreter="latex");
title("fuga", Interpreter="latex");
set(gca, tickLabelInterpreter="latex");
```
でOK
