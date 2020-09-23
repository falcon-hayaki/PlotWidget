
[TOC]

# Plotter based on D3.js

## Target

- [x] Scatter plot
- [x] Histogram plot
- [x] Connect to tablestore （由于tablestore后端带有token，不便于放入public repository）
- [ ] Bug fix

## Usage

### Basic

1. 在html的`head`中引入`d3.js`和`PlotWidgets.js`。
   
   ```html
   <script type="text/javascript" src="js/d3.js"></script>
   <script type="text/javascript" src="js/PlotWidgets.js"></script>
   ```

2. 在html中定义plot的`div`容器，并定义容器`id`。图像会自适应div大小。例：
   
   ```html
   <div id="scatter" style="width:'100%'; height:400px;background-color: white;"></div>
   ```

3. 在js代码块`<script>`中调用函数，传入data等参数。例：
   
   ```html
   <script>
       scatterPlot({id: "scatter", dataset: data, r: 2, type: "cluster", legend: true});
       histogramPlot({ id: "histogram", dataset: data_histogram, transverse: false });
   </script>

### Get data from tablestore

1. 后端使用`python`建立本地后端服务器，使用`HHCAd_Client`连接至`tablestore`数据库。本地服务器搭建范例见[test.py](./py/test.py)。

2. 在html的head中引入jquery。

    ```html
    <script src="https://ajax.aspnetcdn.com/ajax/jQuery/jquery-3.5.1.js"></script>
    ```

3. 在js代码块使用ajax连接至后端。例：

    ```js
    $.ajax({
            url: url + "get_data",
            type: "GET",
            dataType: "json",
            success: function (data) {
                console.log(data['data']);
                data_py = data['data'];
                const test = scatterPlot({id: "scatter", dataset: data_py, r: 2, type: "feature", legend: true});
            }
        })
    ```

    - 注：由于ajax是异步调用，因此`scatterPlot`函数的调用不能写在函数外部

## Parameter descriptions

### Scatter

| Parameter | Description |
| :---: | :--- |
| id | div id |
| dataset | see [dataformat](#scatter-format) |
| type | 'cluster' (default)<br>'feature' |
| legend | boolean<br>show legend or not |

### Histogram

| Parameter | Description |
| :---: | :--- |
| id | div id |
| dataset | see [dataformat](#histogram-format) |
| transverse | boolean |

## data format

### <span id = "scatter-format">Scatter</span>

> A list of lists of lenth 3

```js
var data = [
    [ pos_x_1, pos_y_1, meta_1 ],
    [ pos_x_2, pos_y_2, meta_2 ],
    ...
]
```

### <span id = "histogram-format">Histogram</span>

> A list of dictionary, whose first key should be "group"

```js
var data = [
    {"group": "group_1", "cell_1": "num_11", "cell_2": "num_12", ...},
    {"group": "group_2", "cell_1": "num_21", "cell_2": "num_22", ...},
    ...
]
```

<br>

#### Author

<br>[Xiaoxiao Nong](https://github.com/falcon-hanayori) : falcon_nong@yahoo.com