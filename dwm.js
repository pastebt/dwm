// HtmlTextLink.js

var need_show = false;
var html_content = "";
var final_url = "";


function showFrame(page) {
    need_show = false;
    html_content = html_content + page.frameContent + "\n";
    for (var i = 0; i < page.framesCount; i++) {
        page.switchToFrame(i);
        showFrame(page);
        page.switchToParentFrame();
    }
}


var pageTimeoutFunc = function() {
    if (need_show) {
        // never got to load_finished
        page.switchToMainFrame();
        showFrame(page);
    }
    done_loading();
    phantom.exit();
};


function out_line(data) {
    console.log(data)
}


function done_loading() {
    out_line(html_content);
}


function should_wait(page) {
    var has_refresh = page.evaluate(function () {
        var ms = document.getElementsByTagName('meta');
        for (var i=0; i<ms.length; ++i ) {
            var m = ms.item(i);
            if (m.httpEquiv.toLowerCase() == 'refresh') {
                var t = parseInt(m.content);
                return isNaN(t) ? 0 : t;
            }
        }
        return "norefresh";
    });
    //console.log('has_refresh=' + has_refresh + '; tmo_sec=' + tmo_sec);
    if (!isNaN(has_refresh) && (has_refresh < tmo_sec)) {
        //console.log('should_wait=true');
        return true;
    }
    //console.log(has_refresh);
    // if hase script, and not many content text, wait
    var has_script = page.evaluate(function () {
        var ss = document.getElementsByTagName('script');
        var ii = document.getElementsByTagName('iframe');
        return ss.length + ii.length;
    });
    if (has_script > 0 && html_content.length < 100) {
        return true;
    }
    return tmo_sec < 0
}


function load_finished(status) {
    //console.log(status);
    if (need_show) {
        page.switchToMainFrame();
        showFrame(page);
    }
    if (should_wait(page)) {
        //console.log("loading not finished1");
        return;
    }
    clearTimeout(tmo);
    done_loading();
    //console.log("loading finishedx");
    phantom.exit();
};


/*
 * dwm.js timeout_sec url [referer] [post_data]
 */

var args = require('system').args;
if (args.length < 3 || args.length > 5) {
    console.log("Usage: " + args[0] + " timeout_sec url [referer] [post_data]");
    phantom.exit(0);
}

var tmo_sec = args[1];
var req_url = args[2];
var tmo = setTimeout(pageTimeoutFunc, Math.abs(tmo_sec) * 1000);
var page = require('webpage').create();
//page.settings.userAgent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.4 (KHTML, like Gecko) Safari/537.4';
page.settings.userAgent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.36';
if (args.length == 4) {
    page.customHeaders = {'Referer': args[3]};
}
page.settings.loadImages = false;
page.onLoadFinished = load_finished;
page.onLoadStarted = function() {
    need_show = true;
}
if (args.length == 5) {
    page.open(req_url, 'POST', args[4]);
} else {
    page.open(req_url);
}

