//マウスオーバーしている要素を表示
function mouseover() {
  document.addEventListener("mouseover", function (event) {
    let pref = event.target
    let parent = event.target.parentNode.id;
    if (pref.tagName != "path") {
      parent = "カーソルを合わせると県名を表示します"
    }
    let pref_name_aTag = document.getElementById("pref_name");
    pref_name_aTag.text = parent;

  })
}


function mouseCursor() {
  const mouse = document.getElementById('js-mouse');
  const links = document.querySelectorAll("a");
  let isHovering = false;

  function updateMousePosition(x, y) {
    mouse.style.transform = 'translate(' + x + 'px, ' + y + 'px)';
    mouse.style.opacity = '1';
  }

  function updateMouseStyle() {
    const hoverClass = 'js-hover';
    mouse.classList.toggle(hoverClass, isHovering);
  }

  function handleMouseEnter() {
    isHovering = true;
    updateMouseStyle();
  }

  function handleMouseLeave() {
    isHovering = false;
    updateMouseStyle();
  }

  document.addEventListener('mousemove', function (e) {
    requestAnimationFrame(() => {
      updateMousePosition(e.clientX, e.clientY);
    });
  });

  links.forEach(link => {
    link.addEventListener('mouseenter', handleMouseEnter, false);
    link.addEventListener('mouseleave', handleMouseLeave, false);
  });
}
// ページが読み込まれたらマウスカーソルの処理を開始
//document.addEventListener('DOMContentLoaded', mouseCursor);

//クリックの削除
document.addEventListener('DOMContentLoaded', function () {
  var disableLinkElement = document.getElementById('svg');

  if (disableLinkElement) {
    disableLinkElement.addEventListener('click', function (event) {
      event.preventDefault();
      // ここに他の処理を追加することもできます
    });
  }
});

//クリックしたsvgのリンクを取得
document.addEventListener("DOMContentLoaded", function () {
  document.addEventListener("click", function (event) {
    let parent = event.target.parentNode.classList[1];
    if (event.target.classList[0] == "cls-1") {

      let population = hideColumnsByClass("pref_" + parent.split(".")[0]);
      createHuman(population / 100);
      //県名を表示
      let pref_name = event.target.parentNode.id;
      let prefName = document.querySelector(".prefName");
      prefName.textContent = pref_name;
      //男女比表示
      console.log("parent", parent)
      let malePopulation = document.querySelector('.pref_' + parent + ".row_6").textContent;
      console.log("男性人口", malePopulation);
      let maleRatio = document.querySelector(".male").querySelector(".ratio");
      maleRatio.textContent = (malePopulation / population * 100).toFixed(2) + "%";
      let femalePopulation = document.querySelector('.pref_' + parent + ".row_7").textContent;
      console.log("女性人口", femalePopulation);
      let femaleRatio = document.querySelector(".female").querySelector(".ratio");
      femaleRatio.textContent = (femalePopulation / population * 100).toFixed(2) + "%";
    }
  })
})


function openArticle() {
  document.addEventListener("click", function (event) {
    let clicked = event.target;
    //console.log(clicked);
    if (clicked.getAttribute("class") == "articles") {
      let href = clicked.querySelectorAll("a")[0].getAttribute("href")
      window.location.href = href;
    }
  })
}
openArticle()

function getclass() {
  var temp = document.getElementById('hokkaido');
  //console.log(temp.classList[1]);
  console.log("北海道", "pref" + temp.classList[1].split(".")[0])
  hideColumnsByClass("pref" + temp.classList[1].split(".")[0]);
}
getclass();

//summaryTableの左端の行にclass属性summaryHeaderを付加
function addSummaryHeaderClass() {
  let table = document.querySelector('.summaryTable');

  // 最初のtr要素を取得
  let rows = table.querySelectorAll('tr');

  // 各行の最初のtd要素にsummaryHeaderクラスを付加
  for (let i = 0; i < rows.length; i++) {
    let cells = rows[i].querySelectorAll('td');
    if (cells.length > 0) {
      cells[0].classList.add('summaryHeader');
    }
  }
}
addSummaryHeaderClass();


//都道府県コードを引数に設定し、当てはまるデータ以外を非表示に設定
function hideColumnsByClass(className) {
  let population = "";
  var columns = document.querySelectorAll(".summaryTr")
  columns.forEach(function (column) {
    //console.log(Number(column.classList[1]))

    if (column.classList[1] == className || column.classList[1] == "pref_都道府県コード" || column.classList[1] == "pref_0") {
      column.style.display = "";
      if (column.classList[2] == "row_5") {
        population = column.textContent
      }
    } else {
      column.style.display = "none";
    }
  })
  console.log("人口", population);
  return Number(population)
}

function moveTo() {
  let elements = document.querySelectorAll(".cls-1");
  elements.forEach(function (element) {
    element.addEventListener("click", function (event) {
      //サマリのhiddenを削除
      let summary = document.querySelector(".summary");
      summary.hidden = false
      const targetElement = document.querySelector(".summary");
      //指定した要素までスクロール
      //targetElement.scrollIntoView({ behavior: 'smooth' });
      // 対象の要素までの垂直方向の距離を計算
      const distanceToElement = targetElement.getBoundingClientRect().top + window.scrollY;
      //console.log(distanceToElement);
      window.scrollTo({
        top: distanceToElement * 0.8, // 上端からのピクセル単位の座標
        behavior: 'smooth' // スムーズなスクロール効果を追加する場合
      });
    })
  })

}
moveTo();

function enableEdit(button) {
  var cell = button.parentNode;
  var row = cell.parentNode;
  var columnIndex = Array.from(row.children).indexOf(cell);
  //tableタグ全体を取得
  var tbody = document.querySelector('.csvTable tbody');

  // tbody内の各行の3列目のinput要素のdisabled属性を削除
  let query = 'td:nth-child(' + (columnIndex + 1).toString() + ') input'
  var inputsInThirdColumn = tbody.querySelectorAll(query);
  inputsInThirdColumn.forEach(function (input) {
    input.removeAttribute('readonly');
  });
}
function lockEdit(button) {
  var cell = button.parentNode;
  var row = cell.parentNode;
  var columnIndex = Array.from(row.children).indexOf(cell);
  var tbody = document.querySelector('.csvTable tbody');

  // tbody内の各行の3列目のinput要素のdisabled属性を削除
  let query = 'td:nth-child(' + (columnIndex + 1).toString() + ') input'
  var inputsInThirdColumn = tbody.querySelectorAll(query);
  inputsInThirdColumn.forEach(function (input) {
    input.setAttribute('readonly', true)
  });
}
function addRowCol() {
  let table = document.querySelector(".csvTable")
  let rows = table.rows.length;
  var columnCount = table.rows[0].cells.length;
  var newRow = table.insertRow(rows - 1);
  for (var i = 0; i < columnCount; i++) {
    var cell = newRow.insertCell(i);
    var input = document.createElement("input");
    input.type = "text";
    input.name = "row" + (rows - 2).toString() + "-col" + (i + 1);
    input.classList.add("tableBody");
    input.readOnly = true;
    cell.appendChild(input);
  }
  setRowColValue();
  alert("行の追加完了");
}
function setRowColValue() {
  var table = document.querySelector(".csvTable");
  let numRows = table.rows.length;
  var numCols = table.rows[0].cells.length;
  document.getElementById("numRows").value = numRows - 2;
  document.getElementById("numCols").value = numCols;
  //console.log(numRows-2,numCols)
}

function disableEnterKeySubmit(event) {
  if (event.key === "Enter") {
    event.preventDefault();
    return false;
  }
}

//引数にとった数だけ人型を表示
function createHuman(num) {
  let div = document.querySelector(".canvas");
  while (div.firstChild) {
    div.removeChild(div.firstChild);
  }
  for (var i = 0; i < num; i++) {
    var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("class", "human");
    svg.setAttribute("data-name", "2");
    svg.setAttribute("xmlns", "http://www.w3.org/2000/svg");
    svg.setAttribute("viewBox", "150 0 210 512");

    // パス要素を作成
    var path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", "M256,85.55c23.64,0,42.78-19.16,42.78-42.77C298.78,19.14,279.64,0,256,0S213.22,19.14,213.22,42.78C213.22,66.39,232.36,85.55,256,85.55Z M312.2,97.62H199.81c-20.73,0-43.27,22.55-43.27,43.28v143.77c0,10.36,8.4,18.77,18.76,18.77s18.77-8.4,18.77-18.77v-118.21h8.65v320.88c0,13.62,11.04,24.65,24.64,24.65s24.66-11.03,24.66-24.65v-186.21h7.96v186.21c0,13.62,11.03,24.65,24.66,24.65s24.64-11.03,24.64-24.65V166.47h8.67v118.21c0,10.36,8.4,18.77,18.76,18.77s18.76-8.4,18.76-18.77v-143.77c0-20.73-22.55-43.28-43.27-43.28Z");

    // SVG要素をHTMLに追加
    document.body.appendChild(svg);
    svg.appendChild(path);
    div.appendChild(svg)
  }
}

//サマリ非表示ボタン
function hideTable(button) {
  let parent = button.parentNode.parentNode;
  parent.hidden = true
}

function addColumn() {
  function appendHeader() {
    let newName = prompt("新しく追加する項目を入力してください:");
    console.log(newName);
    console.log("addcolumn")
    let table = document.querySelector(".csvTable")
    let rows = table.rows.length;
    var columnCount = table.rows[0].cells.length;
    let tableHeader = document.querySelector(".csvTable>thead>tr");
    let newHeader = document.createElement("th");
    let newInput = document.createElement("input");
    newInput.name = "tableHeader";
    newInput.value = newName
    newInput.classList.add("tableHeader");
    newInput.setAttribute('onkeypress', "return disableEnterKeySubmit(event)")
    newInput.readOnly = true;
    newHeader.appendChild(newInput);
    tableHeader.appendChild(newHeader);
    return tableHeader.querySelectorAll("th").length
    
  }
  function appendEditButton(num){
    let editBtns = document.querySelectorAll(".csvTable>tbody>tr");
    let newEditBtn = document.createElement("td");
    let newBtn = document.createElement("button");
    newBtn.type = "button";
    newBtn.classList.add("edit");
    newBtn.setAttribute("onclick", "enableEdit(this)")
    newBtn.textContent = "edit Column" + num.toString();
    newEditBtn.appendChild(newBtn);
    editBtns[0].appendChild(newEditBtn);
    console.log(editBtns)
  }
  function appendLockButton(num){
    let editBtns = document.querySelectorAll(".csvTable>tbody>tr");
    let newEditBtn = document.createElement("td");
    let newBtn = document.createElement("button");
    newBtn.type = "button";
    newBtn.classList.add("edit");
    newBtn.setAttribute("onclick", "enableEdit(this)")
    newBtn.textContent = "lock Column" + num.toString();
    newEditBtn.appendChild(newBtn);
    editBtns[editBtns.length-1].appendChild(newEditBtn);
    console.log(editBtns)
  }
  function appendContents(num){
    let contentsTr = document.querySelectorAll(".csvTable>tbody>.tableContents");
    console.log(contentsTr);
    contentsTr.forEach(tr => {
      let newCol = document.createElement("td");
      let newInput = document.createElement("input");
    })
  }

  let num = appendHeader();
  appendEditButton(num);
  appendLockButton(num);
  appendContents(num)
}