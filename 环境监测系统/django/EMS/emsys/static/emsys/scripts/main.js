//!function () {
    var timer = null,getting = false, realTime = true;
    var papers = {
        position: [],
        item: []
    };
    var unit = {s: 1000, m: 1000*60, h: 1000*60*60, d: 1000*60*60*24};
    var colors = ['#f30a0a', '#380af3', '#f30ad7', '#0af3d2', '#f3c00a', '#25f30a']
    function Paper(k, j) {
        var this_ = this;
        this.type = k;
        this.id = j;
        this.wrap = newElem('div');
        this.paper = Raphael(this.wrap, 500, 220);
        document.getElementById('graphs').appendChild(this.wrap);

        var h4 = newElem('h4');
        h4.appendChild(newText(ctrl[k][j].nextSibling.innerHTML));
        prepend(this.wrap, h4);

        this.paper.canvas.addEventListener('mousemove', function(e) {
            var x = e.offsetX || e.layerX,
                y = e.offsetY || e.layerY;
            if (x < 96 || x > 420 || y < 56 || y > 175) {
                this_.hideData();
            } else if (this_.on) {
                this_.showData(x);
            }
        });
        this.paper.canvas.addEventListener('mouseleave', function(e) {
            this_.hideData();
            this_.on = 0;
            each(this_.curves, function (i) {
                this.path.attr({'stroke-width':1});
            });
        });
    }

    Paper.prototype = {
        constructor: Paper,
        init: function () {
            this.num = 0;
            this.on = 0;
            this.paper.clear();
            this.curves = [];
            this.paper.path(['M', 95.5, 55.5, 95.5, 175.5, 420.5, 175.5]).attr({stroke:"#C0D0E0"});
            this.paper.path(['M', 95.5, 145.5, 420.5, 145.5, 'M', 95.5, 115.5, 420.5, 115.5, 'M', 95.5, 85.5, 420.5, 85.5, 'M', 95.5, 55.5, 420.5, 55.5]).attr({stroke:"#D8D8D8"});

            this.dot = this.paper.circle(200.5, 50.5, 4).attr({fill: 'red', 'stroke': 'red', 'stroke-opacity': 0.3, 'stroke-width': 7}).hide();
            this.text = this.paper.text(420.5, 25.5, '').attr({}).hide();
        },
        draw: function () {
            var X = [90.5, 425.5, 55.5, 460.5];
            var posi = [[110.5, 15.5], [260.5, 15.5], [110.5, 35.5], [260.5, 35.5]];

            if (this.type === 'position') {
                for (var i = 0, len = data.curves[this.id].length; i < len; i++) {
                    var data_ = data.curves[this.id][i];
                    if (control.item[i]) {
                        this.curves.push({});
                        var axisY = this.curves[this.num].axisY = getStepY(data_.points);
                        this.curves[this.num].data = data_.points;

                        var info = this.curves[this.num].info = {};
                        info.posi = ctrl.position[this.id].nextSibling.innerHTML;
                        info.item = ctrl.item[i].nextSibling.innerHTML;
                        info.unit = ctrl.item[i].getAttribute('data-unit');

                        for (var j = 0; j < 5; j++) {
                            this.paper.text(X[this.num], 175.5-(j*30), axisY.start + axisY.step*j).attr({'font-size': 12, 'text-anchor': (this.num % 2) ? 'start' : 'end', 'fill': colors[this.num]});
                        }
                        this.paper.circle(posi[this.num][0], posi[this.num][1], 7).attr({'fill': colors[this.num], 'stroke': 'none'});
                        var text = '';
                        text += info.item + '('+info.unit+')';
                        this.paper.text(posi[this.num][0]+16, posi[this.num][1], text).attr({'font-size': 12, 'text-anchor': 'start'});

                        this.num++;
                    }
                }
            } else {
                var arr = [], axisY = {};
                for (var i = 0, len = data.curves.length; i < len; i++) {
                    var data_ = data.curves[i][this.id];
                    if (control.position[i]) {
                        this.curves.push({});
                        this.curves[this.num].axisY = axisY;
                        this.curves[this.num].data = data_.points;
                        arr = arr.concat(data_.points);

                        var info = this.curves[this.num].info = {};
                        info.posi = ctrl.position[i].nextSibling.innerHTML;
                        info.item = ctrl.item[this.id].nextSibling.innerHTML;
                        info.unit = ctrl.item[this.id].getAttribute('data-unit');

                        this.paper.circle(posi[this.num][0], posi[this.num][1], 7).attr({'fill': colors[this.num], 'stroke': 'none'});
                        var text = '';
                        text += info.posi;
                        this.paper.text(posi[this.num][0]+16, posi[this.num][1], text).attr({'font-size': 12, 'text-anchor': 'start'});

                        this.num++;
                    }
                    axisY.start = getStepY(arr).start;
                    axisY.step = getStepY(arr).step;
                }
                for (var j = 0; j < 5; j++) {
                    this.paper.text(X[0], 175.5-(j*30), axisY.start + axisY.step*j).attr({'font-size': 12, 'text-anchor': 'end'});
                }
                this.paper.text(70.5, 37.5, '('+info.unit+')').attr({'text-anchor': 'end'});
            }

            this.drawAxisX();
            this.drawCurves();
        },
        drawAxisX: function () {
            var labelLen,
                delta = data.end - data.start,
                t = new Date(),
                dt = t.getTimezoneOffset()*unit.m;
            if (delta <= 3*unit.h) {
                labelLen = 10*Math.ceil(delta/unit.h)*unit.m;
            } else if (delta <= unit.d) {
                labelLen = Math.ceil(delta/unit.h/6)*unit.h;
            } else if (delta <= 3*unit.d) {
                labelLen = 12*unit.h;
            } else {
                labelLen = Math.ceil(delta/unit.d/6)*unit.d;
            }
            for (var i = 0; i < data.step_num; i++) {
                t.setTime(i*data.step + data.start);
                if ((-dt + t.getTime())%labelLen == 0) {
                    var text;
                    if ((-dt + t.getTime())%unit.d == 0) {
                        text = (t.getMonth()+1)+'-'+t.getDate();
                    } else {
                        text = t.getHours()+':'+t.getMinutes();
                    }
                    var x = Math.floor(98.5+320*i/data.step_num)+0.5;
                    this.paper.text(x, 195.5, text).attr({'font-size': 12, 'text-anchor': 'middle'});
                    this.paper.path(['M', x, 175.5, x, 187.5]).attr({stroke:"#C0D0E0"});
                }
            }
        },
        drawCurves: function () {
            var curves = this.curves, paper_ = this;
            for (var i = 0, len = curves.length; i < len; i++) {
                var curve = curves[i], path = [], flag = 0;
                for (var j = 0, l = data.step_num+1; j < l; j++) {
                    if (curve.data[j] == null) {
                        flag = 0;
                    } else {
                        if (flag) {
                            path.push(98.5+320*j/data.step_num);
                            path.push(175.5-(curve.data[j]-curve.axisY.start)/curve.axisY.step*30);
                        } else {
                            flag = 1;
                            path.push('M');
                            path.push(98.5+320*j/data.step_num);
                            path.push(175.5-(curve.data[j]-curve.axisY.start)/curve.axisY.step*30);
                            path.push('R');
                        }
                    }
                }
                curve.path = this.paper.path(path).attr({stroke: colors[i]});
                curve.path.data('i', i+1)
                curve.path.hover(function(e) {
                    this.toFront();
                    paper_.on = this.data('i');
                    each(curves, function (i) {
                        this.path.attr({'stroke-width':1});
                    });
                    this.attr({'stroke-width':2});
                }, function () {

                });
            }
        },
        showData: function (x) {
            var j = Math.round((x-98.5)/320*data.step_num);
            if (j<0) j = 0;
            if (j>data.step_num) j = data.step_num;
            var i = this.on-1;
            var curve = this.curves[i];
            if (curve.data[j] != null) {
                var cx = 98.5+320*j/data.step_num,
                    cy = 175.5-(curve.data[j]-curve.axisY.start)/curve.axisY.step*30;
                this.dot.attr({cx: cx, cy: cy, fill: colors[i], stroke: colors[i]}).show().toFront();
                var t = new Date(data.start+j*data.step);
                var time = PreInt(t.getMonth()+1,2)+'-'+PreInt(t.getDate(),2);
                if (data.step < unit.d)
                    time += ' ' + PreInt(t.getHours(),2)+':'+PreInt(t.getMinutes(),2);
                if (data.step < unit.m)
                    time += ':'+PreInt(t.getSeconds(),2);
                var text = time + '\n' + curve.data[j] + curve.info.unit;
                this.text.attr({'text': text}).show().toFront();
            }
        },
        hideData: function () {
            if (this.dot) {
                this.dot.hide();
                this.text.hide();
            }
        }
    };

    function getStep(step) {
        var match = step.match(/(\d+)(\D)/);
        return parseFloat(match[1]) * unit[match[2]];
    }
    function getStepY(arr) {
        var max = 0, min = 0;
        var result = {start: 0, step: 1};
        for (var i = 0, len = arr.length; i < len; i++) {
            if (arr[i] > max) max = arr[i];
            if (arr[i] < min) min = arr[i];
        }
        max = max*1.1, min = min*1.1;
        if (max == 0 && min == 0) {
            return result;
        }

        var delta = max-min, step = delta/4, stepStr = step.toString().split('.'), pow;
        if (stepStr[0] !== '0') {
            pow = stepStr[0].length - 1;
            result.step = (Math.floor(step/Math.pow(10, pow))+1)*Math.pow(10, pow);
        } else if (stepStr[1]) {
            pow = -(stepStr[1].match(/^0*/)[0].length + 1);
            result.step = (Math.floor(step/Math.pow(10, pow))+1)*Math.pow(10, pow);
        }
        if (min != 0) {
            result.start = Math.floor(min/result.step*10)*result.step/10;
        }
        return result;
    }

    Paper.init = function () {
        Paper.each(function(k, j) {
            papers[k][j] = new Paper(k, j);

            if (k === 'position') {
                data.curves[j] = [];
            } else {
                for (var i = 0, len = data.curves.length; i < len; i++) {
                    data.curves[i].push({start: 0, end: 0, points: []});
                }
            }
        });

        Paper.changeState();

        $.ajax({
            url: '/emsys/ajax/',
            data: {},
            dataType: 'json',
            success: function(json) {
                data.setTime(json);
                Paper.show();
                addEvent(ctrl.panel, 'change', function () {
                    Paper.changeState();
                    Paper.show();
                });
                timer = setInterval(Paper.refresh, data.step);
                $('#realtime').click(Paper.realTime);
                $('#choosetime').click(Paper.chooseTime);
            }
        });
    };
    Paper.each = function (fn) {
        for (var i = 0; i < 2; i++) {
            var k = ['position', 'item'][i];
            for (var j = 0, len = ctrl[k].length; j < len; j++) {
                if (papers[k] && papers[k][j]) {
                    fn.call(papers[k][j], k, j);
                } else {
                    fn(k, j);
                }
            }
        }
    };
    Paper.changeState = function () {
        control.type = ctrl.radios[1].checked ? 'item' : 'position';
        Paper.each(function (k, j) {
            control[k][j] = ctrl[k][j].checked;
        });
    };
    Paper.show = function () {
        Paper.each(function (k, j) {
            if (k !== control.type || !control[k][j]) {
                this.wrap.style.display = 'none';
            } else {
                this.init();
                this.draw();
                this.wrap.style.display = 'block';
            }
        });
    };
    Paper.refresh = function () {
        if (getting) return;
        getting = true;
        var t = getTimeF(new Date(data.end+data.step));
        $.ajax({
            url: '/emsys/ajax/',
            data: {
                start: t
            },
            dataType: 'json',
            success: function (json) {
                getting = false;
                if (!realTime) return;
                var len = json[ctrl.position[0].value+''+ctrl.item[0].value].length;
                data.start += len*data.step;
                data.end += len*data.step;
                for (var k = 0; k < len; k++) {
                    for (var i = 0; i < data.curves.length; i++) {
                        for (var j = 0; j < data.curves[i].length; j++) {
                            data.curves[i][j].points.shift();
                            data.curves[i][j].points.push(json[ctrl.position[0].value+''+ctrl.item[0].value][k]);
                        }
                    }
                }
                Paper.show();
            },
            error: function () {
                getting = false;
            }
        });
    };
    Paper.realTime = function () {
        if (realTime || getting) return;
        realTime = true;
        Paper.each(function(){
            this.init();
        });
        $.ajax({
            url: '/emsys/ajax/',
            data: {},
            dataType: 'json',
            success: function(json) {
                if (!realTime) return;
				$('#realtime').addClass('on');
                data.setTime(json);
                Paper.show();
                clearInterval(timer);
                timer = setInterval(Paper.refresh, data.step);
            },
            error: function () {
                location.reload();
            }
        });
    };
    Paper.chooseTime = function () {
        realTime = false;
        clearInterval(timer);
        var fla = $('.flatpickr');
        var t1 = new Date(fla.eq(0).val());
        var t2 = new Date(fla.eq(1).val());
        if(t1-t2>0) {
            ChTime[0].setDate(t2);
            ChTime[1].setDate(t1);
        }
        Paper.each(function(){
            this.init();
        });
        $.ajax({
            url: '/emsys/ajax/',
            data: {
                start: fla.eq(0).val(),
                end: fla.eq(1).val()
            },
            dataType: 'json',
            success: function(json) {
                if (realTime) return;
				$('#realtime').removeClass('on');
                ChTime[0].setDate(json.start);
                ChTime[1].setDate(json.end);
                data.setTime(json);
                Paper.show();
            },
            error: function () {
                location.reload();
            }
        });
    }

    var control = {
        type: 0,
        position: [],
        item: []
    };
    var ctrl = {
        panel: document.getElementById('control-panel'),
        radios: document.getElementsByName('groupby'),
        position: document.getElementsByName('position'),
        item: document.getElementsByName('item')
    };
    var data = {
        start: 0, end: 0,
        step: 0, step_num: 0,
        curves: []
    };
    data.setTime = function (d) {
        data.start = new Date(d.start).getTime(), data.end = new Date(d.end).getTime();
        data.step = getStep(d.step);
        data.step_num = (data.end-data.start)/data.step;
        for (var i = 0; i < data.curves.length; i++) {
            for (var j = 0; j < data.curves[i].length; j++) {
                data.curves[i][j].points = d[ctrl.position[i].value+''+ctrl.item[j].value];
            }
        }
    }

    Paper.init();
//}();