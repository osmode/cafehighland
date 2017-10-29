var aNetworkLog = [];

chrome.webRequest.onCompleted.addListener(function(oCompleted) {
            var sCompleted = JSON.stringify(oCompleted);
            aNetworkLog.push(sCompleted);
        }
        ,{urls: ["http://*/*"]}
 );

chrome.extension.onConnect.addListener(function (port) {
    port.onMessage.addListener(function (message) {
        if (message.action == "getNetworkLog") {
            port.postMessage(aNetworkLog);
        }
    });
});