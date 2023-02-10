function g_ex2() {
  const SS = "SS";
  const FR = "FR";
  const imageUrls = {};
  const rootFolderId = "1meOef4dAt53zfCzIAB1PC5evIm5_l1Wy";
  const lFolders = DriveApp.getFolderById(rootFolderId).getFolders();
  while (lFolders.hasNext()) {
    const layout = lFolders.next();
    const layoutName = layout.getName();
    if (!(layoutName in imageUrls)) {
      imageUrls[layoutName] = {};
    }
    const qFolders = layout.getFolders();
    while (qFolders.hasNext()) {
      const question = qFolders.next();
      const questionName = question.getName();
      if (!(questionName in imageUrls[layoutName])) {
        imageUrls[layoutName][questionName] = {};
      }
      const dFolders = question.getFolders();
      while (dFolders.hasNext()) {
        const dataset = dFolders.next();
        const datasetName = dataset.getName();
        if (!(datasetName in imageUrls[layoutName][questionName])) {
          imageUrls[layoutName][questionName][datasetName] = {};
        }
        const images = dataset.getFiles();
        while (images.hasNext()) {
          const image = images.next();
          const imageName = image.getName();
          const imageNumber = imageName.replace(".png", "");
          const imageUrl = image.getUrl();
          imageUrls[layoutName][questionName][datasetName][imageNumber] =
            imageUrl;
        }
      }
    }
  }
  const keys = {
    [FR]: Object.keys(imageUrls[FR]).sort(),
    [SS]: Object.keys(imageUrls[SS]).sort(),
  };
  for (let i = 0; i < keys[FR].length; ++i) {
    const questionIds = { [FR]: keys[FR][i], [SS]: keys[SS][i] };
    console.log(questionIds);
    const formTitle = `評価実験その1-${i + 1}`;
    createEx2Form(formTitle, imageUrls, questionIds);
  }
}

function createEx2Form(formTitle, imageUrls, questionIds) {
  const formDescription = `実験へのご協力ありがとうございます。
下記の説明を読んだ上で実験に進んでください。


これは最適化アプローチを用いて生成したパラメータの評価のための実験です。

実験では下記の3種類のパラメータと、Fruchterman-ReingoldまたはSparse-Sgdを用いて生成した描画結果を下記の3種類のパラメータごとに4個ずつ、合計12個表示します。
最適化アプローチを用いて生成されたパラメータ
経験的に良いとされるパラメータ
ランダムに生成されたパラメータ

回答者にはリンク先に表示された12個の描画結果から「好み」のものを4個選択していただきます。

実験では2種類の描画アルゴリズムと3種類のグラフについて上記操作を5回ずつ、合計30回の回答をお願いします。


また描画結果の「好み」は、主観的に好ましいと感じたもので結構です。
例えばノードの配置やエッジの明瞭さなどの一般的な基準をもとにしたものでも、芸術的な美しさや「パット見いい感じ」みたいな好ましさであっても構いません。`;

  const SS = "SS";
  const FR = "FR";
  const drawingNameMap = { FR: "Fruchterman-Reingold", SS: "Sparse-Sgd" };
  const form = FormApp.create(formTitle);
  form.setDescription(formDescription);
  const placement_numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
  const qIds = [1, 2, 3, 4, 5];
  const ls = [FR, SS];
  const ds = ["les_miserables", "1138_bus", "USpowerGrid"];

  const inputItem = form.addTextItem();
  inputItem.setTitle("氏名");
  inputItem.setRequired(true);

  const checkBoxValidation = FormApp.createCheckboxValidation()
    .setHelpText("4個選択してください。")
    .requireSelectExactly(4)
    .build();
  for (const l of ls) {
    for (const d of ds) {
      const pageBreak = form.addPageBreakItem();
      pageBreak
        .setTitle(`${d}グラフを${drawingNameMap[l]}で描画した結果の評価`)
        .setHelpText(
          "リンクから描画結果を確認して、好ましいと感じる描画結果の番号を4個選択してください。"
        );
      for (const qId of qIds) {
        const item = form.addCheckboxItem();
        item.setTitle(`${l}:${questionIds[l]}:${d}:${qId}`);
        item.setHelpText(`${imageUrls[l][questionIds[l]][d][qId]}`);
        item.setChoiceValues(placement_numbers);
        item.setValidation(checkBoxValidation);
        item.setRequired(true);
      }
    }
  }
  const pageBreak = form.addPageBreakItem();
  pageBreak.setHelpText(`フォームを送信して評価実験を終了してください。
ご協力ありがとうございました。`);
}
