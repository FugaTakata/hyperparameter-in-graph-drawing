# ハイパーパラメータ最適化実験

## optimization.py
- 9つの評価指標を同時に最適化する

## generate_randomized.py
- 指定した数のランダムなパラメータを生成し、0-100のseedで描画した時の評価指標を計測する

## parcoords
- https://www.react-graph-gallery.com/parallel-plot
- 上記リンクを参考に並行座標プロットを作成した

## good_params_boxplot.ipynb
- パレートフロントのうち、全ての評価指標において経験的なHPを上回るHPの可視化

## choice_pareto*.ipynb
- パレート解を評価指標の昇順でindexを振り、indexの合計降順で可視化を表示

## draw_all_graph.ipynb
- 設定したHPですべてのグラフの可視化を表示

## multi_objective*.py
- 多目的最適化を行う

