# 基于D3.js的画图控件

## 简介

该项目为基于[`D3.js`](https://d3js.org/)开发的JavaScript画图控件。用户只需在前端中调用[控件函数](#函数及参数说明)，传入符合[格式](#数据格式)的数据即可。该控件能够自适应其所在div的大小。

## [Demo](http://103.152.132.78:5678/)

## 开发进度

- [x] 散点图
- [x] 条形图
- [x] 条形图（比例形式）
- [x] 弦图
- [x] 通过基于`Flask`的`python`后端连接至`tablestore`
- [ ] 桑基图

## 用法

1. 在html的`head`中引入`d3.js`、`PlotWidgets.js`和`PlotWidgets.css`。
   
   ```html
    <head>
    <script type="text/javascript" src="js/d3.js"></script>
    <script type="text/javascript" src="js/PlotWidgets.js"></script>
    <link rel="stylesheet" type="text/css" href="css/plotWidget.css">
    </head>
   ```

2. 在html中定义plot的`div`容器，并定义容器`id`。图像会自适应div大小。例：
   
   ```html
   <div id="scatter" style="width:'100%'; height:400px;background-color: white;"></div>
   <div id="barplot" style="width:'100%'; height:400px;background-color: white;"></div>
   ```

3. 在js代码块`<script>`中调用函数，传入data等参数。例：
   
   ```html
   <script>
       scatterPlot({id: "scatter", dataset: data_scatter, r: 2, type: "cluster", legend: true});
       barPlot({ id: "barplot", dataset: data_barplot, horizontal: false });
   </script>

## 函数及参数说明

### 1. 散点图

```js
scatterPlot({ id, dataset, r = 5, type = 'cluster', legend = false } = {})
```

| Parameter | Description                       |
| :-------: | :-------------------------------- |
|    id     | div id                            |
|  dataset  | 见 [数据格式](#数据格式) |
|   type    | 散点图类型。分为"cluster"和"feature"。<br>"cluster"用于展示聚类结果，"feature"用于展示数据中某类型的丰度。两者传入的数据格式略有不同。  |
|  legend   | 是否显示图注。`true`或`false`，默认为`false`。<br>（当`cluster`聚类类型过多或名字过长时，可能会出现显示bug，不建议使用。在v2.0中添加了鼠标悬停显示类型的功能，弥补了这一缺陷。）     |

### 2. 柱状图

```js
barPlot({ id, dataset, horizontal = false } = {})
histogramPlot({ id, dataset, horizontal = false } = {})
```

| Parameter  | Description                         |
| :--------: | :---------------------------------- |
|     id     | div id                              |
|  dataset   | 见 [数据格式](#数据格式) |
| transverse | 是否横向显示                             |

### 3. 弦图

```js
chordPlot({ id, matrix, names } = {})
```

| Parameter  | Description                         |
| :--------: | :---------------------------------- |
|     id     | div id                              |
|  matrix   | 表示两个数据之间关系的方阵。见 [数据格式](#数据格式) |
| names | 列名。见 [数据格式](#数据格式) |

## 数据格式

### 散点图

> n行3列的多元列表。第一列为<strong>x轴坐标</strong>，第二列为<strong>y轴坐标</strong>，第三列<strong>聚类类型</strong>（cluster: String）或<strong>丰度</strong>（feature: double）

```js
var data = [
    [ pos_x_1, pos_y_1, meta_1 ],
    [ pos_x_2, pos_y_2, meta_2 ],
    ...
]
```

### 柱状图

> n行字典列表。字典必须包含`group`字段，作为x轴坐标，其余字段为`{"类型名": 数量(int)}`

```js
var data = [
    {"group": "group_1", "cell_1": num_11, "cell_2": "num_12", ...},
    {"group": "group_2", "cell_1": num_21, "cell_2": num_22, ...},
    ...
]
```

### 弦图

> matrix: n*n方阵
> 
> names: n维列表

```js
var matrix = [
          [ 1000,  3045 , 4567 , 1234 , 3714 ],
          [ 3214,  2000 , 2060 , 124  , 3234 ],
          [ 8761,  6545 , 3000 , 8045 , 647  ],
          [ 3211,  1067 , 3214 , 4000 , 1006 ],
          [ 2146,  1034 , 6745 , 4764 , 5000 ]
        ];
var names = [ "北京" , "上海" , "广州" , "深圳" , "香港"  ];
```

<br>

## 连接到`tablestore`

1. 在后台运行`py`目录下的[test.py](./py/test.py)建立本地后端服务器，监听7777端口。<br>python文件中使用`HHCAd_Client`连接至`tablestore`数据库。`HHCAd_Client`更新及使用方法见[这里](https://github.com/falcon-hanayori/HCAd_Client)

2. 在html的head中引入jquery。

    ```html
    <head>
    <script src="https://ajax.aspnetcdn.com/ajax/jQuery/jquery-3.5.1.js"></script>
    </head>
    ```

3. 在js代码块使用ajax连接至后端。例：

    ```js
    $.ajax({
            url: url + "api_get_data",
            type: "GET",
            dataType: "json",
            success: function (data) {
                console.log(data['data']);
                data_py = data['data'];
                const test = scatterPlot({id: "scatter", dataset: data_py, r: 2, type: "feature"});
            }
        })
    ```
    
<br>

## Author

<br>[Xiaoxiao Nong](https://github.com/falcon-hanayori) : falcon_nong@yahoo.com
