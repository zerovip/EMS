if (!Array.prototype.indexOf) {
    Array.prototype.indexOf = function (item) {
        for (var i = 0, len = this.length; i < len; i++) {
            if (this[i] === item) return i;
        }
        return -1;
    }
}
function addEvent( obj, ev, fn, bool ) {
    if ( obj.addEventListener ) {
        obj.addEventListener( ev, fn, bool );
    } else if (obj.attachEvent) {
        if (!addEvent.fns) {
            addEvent.fns = [];
            addEvent.newfns = [];
        }
        var newfn = function(){fn.call(obj)};
        addEvent.fns.push(fn);
        addEvent.newfns.push(newfn);
        obj.attachEvent( 'on'+ev, newfn );
    }
}
function removeEvent( obj, ev, fn, bool ) {
    if ( obj.addEventListener ) {
        obj.removeEventListener( ev, fn, bool );
    } else if (obj.attachEvent) {
        var index = addEvent.fns.indexOf(fn);
        if (index > -1) {
            obj.detachEvent( 'on'+ev, addEvent.newfns[index] );
            addEvent.fns.splice(index, 1);
            addEvent.newfns.splice(index, 1);
        }
    }
}
function prepend(parent, child) {
    if (parent.childNodes.length) {
        parent.insertBefore(child, parent.firstChild);
    } else {
        parent.appendChild(child);
    }
}
function newElem(tag) {
    return document.createElement(tag);
}
function newText(str) {
    return document.createTextNode(str);
}

function each(arr, fn) {
    var len = arr.length, i = 0;
    for (; i < len; i++) {
        fn.call(arr[i], i);
    }
}

/* PrefixInteger */
function PreInt(num, n) {
    return (Array(n).join(0) + num).slice(-n);
}

function getTimeF(date) {
    var y = date.getFullYear(), m = PreInt(date.getMonth()+1,2),
        d = PreInt(date.getDate(),2), h = PreInt(date.getHours(),2),
        min = PreInt(date.getMinutes(),2), s = PreInt(date.getSeconds(),2);
    return y+'-'+m+'-'+d+' '+h+':'+min+':'+s;
}