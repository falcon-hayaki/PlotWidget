function scatterPlot({ id, dataset, r = 5, type = 'cluster', legend = false } = {}) {
    var div = document.getElementById(id);
    var divWidth = parseInt(window.getComputedStyle(div).getPropertyValue('width'));
    var divHeight = parseInt(window.getComputedStyle(div).getPropertyValue('height'));
    var padding = { left: 30, right: 30, top: 20, bottom: 20 };

    // TODO: featureplot 图注
    if (type === 'feature') {
        legend = false;
    }

    if (legend) {
        padding['bottom'] = divHeight / 5;
    }

    // colors
    var schemeRainbow = d3.schemePaired; // len = 12

    var plotWidth = divWidth - padding.left - padding.right;
    var plotHeigh = divHeight - padding.top - padding.bottom;

    // add Suspendion
    var suspension = document.createElement("div");
    var suspension_id = id + "_suspension";
    suspension.setAttribute("class", "chartTooltip hidden");
    suspension.setAttribute("id", suspension_id);
    var sus_p = document.createElement("p");
    sus_p.setAttribute("class", "name")
    suspension.appendChild(sus_p);
    div.appendChild(suspension);

    var x_scale = d3.scaleLinear()
        .domain([d3.min(dataset, function(d) { return d[0]; }), d3.max(dataset, function(d) { return d[0]; })])
        .range([0, plotWidth]);
    var y_scale = d3.scaleLinear()
        .domain([d3.min(dataset, function(d) { return d[1]; }), d3.max(dataset, function(d) { return d[1]; })])
        .range([plotHeigh, 0]);

    if (type === 'cluster') {
        var z_scale = d3.scaleOrdinal()
            .domain(data.map(d => d[2]))
            .range(schemeRainbow);
    } else if (type === 'feature') {
        dataset = dataset.sort((x, y) => (x[2] - y[2]))

        var z_scale = d3.scaleLinear()
            .domain([d3.min(dataset, function(d) { return d[2]; }), d3.max(dataset, function(d) { return d[2]; })])
            .range(["#d9d9d9", "#0002FF"]);
    }

    var x_axis = d3.axisBottom(x_scale)
        .ticks(7);
    var y_axis = d3.axisLeft(y_scale)
        .ticks(7);

    var svg = d3.select("#" + id)
        .append("svg")
        .attr("width", "100%")
        .attr("height", "100%");

    svg.selectAll("circle")
        .data(dataset)
        .enter()
        .append("circle")
        .attr("transform", "translate(" + padding.left + "," + padding.top + ")")
        .attr("cx", function(d) {
            return x_scale(d[0]);
        })
        .attr("cy", function(d) {
            return y_scale(d[1]);
        })
        .attr("fill", function(d) {
            return z_scale(d[2]);
        })
        .attr("r", r)
        .on("mouseover", function(event, d, i) {
            let yPosition = event.screenY - 80;
            let xPosition = event.screenX;

            var chartTooltip = d3
                .select("#" + suspension_id)
                .style("left", xPosition + "px")
                .style("top", yPosition + "px")
                .style("background-color", z_scale(d[2]));

            chartTooltip.select(".name").html(d[2]);
            chartTooltip.classed("hidden", false);
        })
        .on("mouseout", function(d) {
            d3.select("#" + suspension_id).classed("hidden", true);
        });

    svg.append("g")
        .attr("fill", "none")
        .attr("font-family", "sans-serif")
        .attr("transform", "translate(" + padding.left + "," + (divHeight - padding.bottom) + ")")
        .call(x_axis)
    svg.append("g")
        .attr("fill", "none")
        .attr("font-family", "sans-serif")
        .attr("transform", "translate(" + padding.left + "," + (padding.top) + ")")
        .call(y_axis);

    if (legend) {
        var data_set = Array.from(new Set(dataset.map(d => d[2])));

        var legend_area = svg.append('g')
            .attr('transform', 'translate(0, ' + (divHeight - padding.bottom / 2) + ')');

        var plot_legend = legend_area.selectAll('g')
            .data(data_set)
            .enter()
            .append('g')
            .attr("transform", function(d, i) {
                return "translate(" + i * padding.bottom * 1.5 + ",0)";
            });

        plot_legend.append('rect')
            .attr('width', padding.bottom / 4)
            .attr('height', padding.bottom / 4)
            .attr("fill", function(d, i) {
                return z_scale(d);
            });

        plot_legend.append('text')
            .attr('x', padding.bottom / 4 + 5)
            .attr('y', padding.bottom / 8)
            .attr("fill", function(d, i) {
                return z_scale(d);
            })
            .attr("dy", ".35em")
            .text(function(d, i) {
                return d;
            });
    }

    return svg;
}

function barPlot({ id, dataset, horizontal = false } = {}) {
    var div = document.getElementById(id);
    var divWidth = parseInt(window.getComputedStyle(div).getPropertyValue('width'));
    var divHeight = parseInt(window.getComputedStyle(div).getPropertyValue('height'));
    var padding = { left: 30, right: 30, top: 20, bottom: 20 };

    var plotWidth = divWidth - padding.left - padding.right;
    var plotHeigh = divHeight - padding.top - padding.bottom;

    // add Suspendion
    var suspension = document.createElement("div");
    var suspension_id = id + "_suspension";
    suspension.setAttribute("class", "chartTooltip hidden");
    suspension.setAttribute("id", suspension_id);
    var sus_p = document.createElement("p");
    sus_p.setAttribute("class", "name")
    suspension.appendChild(sus_p);
    div.appendChild(suspension);

    keys = [];
    for (key in dataset[0]) {
        keys.push(key);
    }
    keys.splice(keys.indexOf("group"), 1);
    keys.splice(keys.indexOf("total"), 1);
    groups = dataset.map(d => d["group"]);

    var total = {}
    for (i in keys) {
        t = 0;
        for (j in dataset) {
            t += dataset[j][keys[i]];
        }
        total[keys[i]] = t
    }

    var z = d3.scaleOrdinal()
        .domain(groups)
        .range(d3.schemePaired);

    var svg = d3.select("#" + id)
        .append("svg")
        .attr("width", "100%")
        .attr("height", "100%");

    if (horizontal) {
        var x0 = d3.scaleBand()
            .domain(keys)
            .rangeRound([plotHeigh, 0])
            .padding(0.1);

        svg.append("g")
            .selectAll("g")
            .data(keys)
            .join("g")
            .attr("transform", d => `translate(0, ${x0(d)})`)
            .selectAll("rect")
            .data(key => dataset.map(d => ({ group: d["group"], value: d[key], "key": key })))
            .join("rect")
            .attr("transform", "translate(" + padding.left + "," + padding.top + ")")
            .attr("x", function(d, i) {
                let y = 0;
                for (let j = 0; j < i; j++) {
                    y += (dataset[j][d["key"]] / total[d["key"]] * plotWidth);
                }
                return y;
            })
            .attr("height", x0.bandwidth())
            .attr("width", (d, i) => dataset[i][d["key"]] / total[d["key"]] * plotWidth)
            .attr("fill", d => z(d.group))
            .on("mouseover", function(event, d, i) {
                let yPosition = event.screenY - 80;
                let xPosition = event.screenX;

                var chartTooltip = d3
                    .select("#" + suspension_id)
                    .style("left", xPosition + "px")
                    .style("top", yPosition + "px")
                    .style("background-color", z(d.group));

                chartTooltip.select(".name").html(d["group"] + " <br> count: " + d["value"] + "; " + (d["value"] / total[d["key"]] * 100).toFixed(2) + "%");
                chartTooltip.classed("hidden", false);
            })
            .on("mouseout", function(d) {
                d3.select("#" + suspension_id).classed("hidden", true);
            })

        var x_axis = d3.axisLeft(x0)
            .ticks(7);

        svg.append("g")
            .attr("fill", "none")
            .attr("font-family", "sans-serif")
            .attr("transform", "translate(" + padding.left + "," + (padding.top) + ")")
            .call(x_axis);
    } else {
        var x0 = d3.scaleBand()
            .domain(keys)
            .rangeRound([0, plotWidth])
            .padding(0.1);

        svg.append("g")
            .selectAll("g")
            .data(keys)
            .join("g")
            .attr("transform", d => `translate(${x0(d)}, 0)`)
            .selectAll("rect")
            .data(key => dataset.map(d => ({ group: d["group"], value: d[key], "key": key })))
            .join("rect")
            .attr("transform", "translate(" + padding.left + "," + padding.top + ")")
            .attr("x", function(d) {
                return x0(d.group);
            })
            .attr("y", function(d, i) {
                let y = 0;
                for (let j = 0; j < i; j++) {
                    y += (dataset[j][d["key"]] / total[d["key"]] * plotHeigh);
                }
                return y;
            })
            .attr("width", x0.bandwidth())
            .attr("height", function(d, i) {
                return dataset[i][d["key"]] / total[d["key"]] * plotHeigh;
            })
            .attr("fill", d => z(d.group))
            .on("mouseover", function(event, d, i) {
                let yPosition = event.screenY - 80;
                let xPosition = event.screenX;

                var chartTooltip = d3
                    .select("#" + suspension_id)
                    .style("left", xPosition + "px")
                    .style("top", yPosition + "px")
                    .style("background-color", z(d.group));

                chartTooltip.select(".name").html(d["group"] + " <br> count: " + d["value"] + "; " + (d["value"] / total[d["key"]] * 100).toFixed(2) + "%");
                chartTooltip.classed("hidden", false);
            })
            .on("mouseout", function(d) {
                d3.select("#" + suspension_id).classed("hidden", true);
            })

        var x_axis = d3.axisBottom(x0)
            .ticks(7);

        svg.append("g")
            .attr("fill", "none")
            .attr("font-family", "sans-serif")
            .attr("transform", "translate(" + padding.left + "," + (divHeight - padding.bottom) + ")")
            .call(x_axis)
    }

    return svg;
}

function histogramPlot({ id, dataset, horizontal = false, yaxis = false } = {}) {
    var div = document.getElementById(id);
    var divWidth = parseInt(window.getComputedStyle(div).getPropertyValue('width'));
    var divHeight = parseInt(window.getComputedStyle(div).getPropertyValue('height'));
    var padding = { left: 30, right: 30, top: 20, bottom: 20 };

    var plotWidth = divWidth - padding.left - padding.right;
    var plotHeigh = divHeight - padding.top - padding.bottom;

    // add Suspendion
    var suspension = document.createElement("div");
    var suspension_id = id + "_suspension";
    suspension.setAttribute("class", "chartTooltip hidden");
    suspension.setAttribute("id", suspension_id);
    var sus_p = document.createElement("p");
    sus_p.setAttribute("class", "name")
    suspension.appendChild(sus_p);
    div.appendChild(suspension);

    keys = [];
    for (key in dataset[0]) {
        keys.push(key);
    }
    keys = keys.slice(1)
    groups = dataset.map(d => d["group"]);

    var z = d3.scaleOrdinal()
        .domain(groups)
        .range(d3.schemePaired);

    var svg = d3.select("#" + id)
        .append("svg")
        .attr("width", "100%")
        .attr("height", "100%");

    if (horizontal) {
        var x0 = d3.scaleBand()
            .domain(keys)
            .rangeRound([plotHeigh, 0])
            .padding(0.1);
        var x1 = d3.scaleBand()
            .domain(groups)
            .rangeRound([0, x0.bandwidth()])
            .paddingInner(0.05);
        var y = d3.scaleLinear()
            .domain([0, !yaxis ? d3.max(dataset, d => d3.max(keys, key => d[key])) : yaxis])
            .range([0, plotWidth]);

        svg.append("g")
            .selectAll("g")
            .data(keys)
            .join("g")
            .attr("transform", d => `translate(0, ${x0(d)})`)
            .selectAll("rect")
            .data(key => dataset.map(d => ({ group: d["group"], value: d[key] })))
            .join("rect")
            .attr("transform", "translate(" + padding.left + "," + padding.top + ")")
            .attr("x", function(d) {
                return 0;
            })
            .attr("y", function(d) {
                return x1(d.group);
            })
            .attr("height", x1.bandwidth())
            .attr("width", d => y(d.value))
            .attr("fill", d => z(d.group))
            .on("mouseover", function(event, d, i) {
                let yPosition = event.screenY - 80;
                let xPosition = event.screenX;

                var chartTooltip = d3
                    .select("#" + suspension_id)
                    .style("left", xPosition + "px")
                    .style("top", yPosition + "px")
                    .style("background-color", z(d.group));

                chartTooltip.select(".name").html(d["group"] + " <br> count: " + d["value"]);
                chartTooltip.classed("hidden", false);
            })
            .on("mouseout", function(d) {
                d3.select("#" + suspension_id).classed("hidden", true);
            });

        var x_axis = d3.axisLeft(x0)
            .ticks(7);
        var y_axis = d3.axisBottom(y)
            .ticks(7);

        svg.append("g")
            .attr("fill", "none")
            .attr("font-family", "sans-serif")
            .attr("transform", "translate(" + padding.left + "," + (divHeight - padding.bottom) + ")")
            .call(y_axis)
        svg.append("g")
            .attr("fill", "none")
            .attr("font-family", "sans-serif")
            .attr("transform", "translate(" + padding.left + "," + (padding.top) + ")")
            .call(x_axis);
    } else {
        var x0 = d3.scaleBand()
            .domain(keys)
            .rangeRound([0, plotWidth])
            .padding(0.1);
        var x1 = d3.scaleBand()
            .domain(groups)
            .rangeRound([0, x0.bandwidth()])
            .paddingInner(0.05);
        var y = d3.scaleLinear()
            .domain([0, d3.max(dataset, d => d3.max(keys, key => d[key]))])
            .range([plotHeigh, 0]);

        svg.append("g")
            .selectAll("g")
            .data(keys)
            .join("g")
            .attr("transform", d => `translate(${x0(d)}, 0)`)
            .selectAll("rect")
            .data(key => dataset.map(d => ({ group: d["group"], value: d[key] })))
            .join("rect")
            .attr("transform", "translate(" + padding.left + "," + padding.top + ")")
            .attr("x", function(d) {
                return x1(d.group);
            })
            .attr("y", function(d) {
                return y(d.value);
            })
            .attr("width", x1.bandwidth())
            .attr("height", d => plotHeigh - y(d.value))
            .attr("fill", d => z(d.group))
            .on("mouseover", function(event, d, i) {
                let yPosition = event.screenY - 80;
                let xPosition = event.screenX;

                var chartTooltip = d3
                    .select("#" + suspension_id)
                    .style("left", xPosition + "px")
                    .style("top", yPosition + "px")
                    .style("background-color", z(d.group));

                chartTooltip.select(".name").html(d["group"] + " <br> count: " + d["value"]);
                chartTooltip.classed("hidden", false);
            })
            .on("mouseout", function(d) {
                d3.select("#" + suspension_id).classed("hidden", true);
            });

        var x_axis = d3.axisBottom(x0)
            .ticks(7);
        var y_axis = d3.axisLeft(y)
            .ticks(7);

        svg.append("g")
            .attr("fill", "none")
            .attr("font-family", "sans-serif")
            .attr("transform", "translate(" + padding.left + "," + (divHeight - padding.bottom) + ")")
            .call(x_axis)
        svg.append("g")
            .attr("fill", "none")
            .attr("font-family", "sans-serif")
            .attr("transform", "translate(" + padding.left + "," + (padding.top) + ")")
            .call(y_axis);
    }

    return svg;
}

function chordPlot({ id, matrix, names } = {}) {
    var div = document.getElementById(id);
    var divWidth = parseInt(window.getComputedStyle(div).getPropertyValue('width'));
    var divHeight = parseInt(window.getComputedStyle(div).getPropertyValue('height'));
    var padding = { left: 30, right: 30, top: 20, bottom: 20 };

    var plotWidth = divWidth - padding.left - padding.right;
    var plotHeigh = divHeight - padding.top - padding.bottom;

    // add Suspendion
    var suspension = document.createElement("div");
    var suspension_id = id + "_suspension";
    suspension.setAttribute("class", "chartTooltip hidden");
    suspension.setAttribute("id", suspension_id);
    var sus_p = document.createElement("p");
    sus_p.setAttribute("class", "name")
    suspension.appendChild(sus_p);
    div.appendChild(suspension);

    var chords = d3.chord()
        (matrix);
    var groups = chords.groups;

    var z = d3.scaleOrdinal()
        .domain(groups.map(d => d.index))
        .range(d3.schemePaired);

    var svg = d3.select("#" + id)
        .append("svg")
        .attr("width", "100%")
        .attr("height", "100%")
        .append("g")
        .attr('transform', 'translate(' + plotWidth / 2 + "," + plotHeigh / 2 + ")");

    // 弧生成器
    var innerRadius = plotHeigh / 2 * 0.7;
    var outerRadius = innerRadius * 1.05;
    var outer_arc = d3.arc()
        .innerRadius(innerRadius)
        .outerRadius(outerRadius);

    var g_outer = svg.append("g");
    g_outer.selectAll("path")
        .data(groups)
        .enter()
        .append("path")
        .style("fill", d => z(d.index))
        .style("stroke", d => {
            return z(d.index);
        })
        .attr("d", outer_arc)
        .on("mouseover", function(event, d, i) {
            let yPosition = event.screenY - 80;
            let xPosition = event.screenX;

            var chartTooltip = d3
                .select("#" + suspension_id)
                .style("left", xPosition + "px")
                .style("top", yPosition + "px")
                .style("background-color", z(d.group));

            chartTooltip.select(".name").html(names[d.index]);
            chartTooltip.classed("hidden", false);
        })
        .on("mouseout", function(d) {
            d3.select("#" + suspension_id).classed("hidden", true);
        });

    // draw chords
    var ribbon = d3.ribbon()
        .radius(innerRadius);

    svg.append("g")
        .attr('class', 'chord')
        .selectAll("path")
        .data(chords)
        .enter()
        .append("path")
        .attr("d", ribbon)
        .attr("fill", ({ source: { index } }) => z(index))
        .attr('stroke', ({ source: { index } }) => d3.rgb(z(index)).darker())
        .on("mouseover", function(event, d, i) {
            let yPosition = event.screenY - 80;
            let xPosition = event.screenX;

            var chartTooltip = d3
                .select("#" + suspension_id)
                .style("left", xPosition + "px")
                .style("top", yPosition + "px")
                .style("background-color", z(d.source.index));

            chartTooltip.select(".name").html("Source: " + names[d.source.index] + "<br>" + "Target: " + names[d.target.index] + "<br>" + "Value: " + d.source.value + " " + d.target.value);
            chartTooltip.classed("hidden", false);
        })
        .on("mouseout", function(d) {
            d3.select("#" + suspension_id).classed("hidden", true);
        })

    return svg;
}