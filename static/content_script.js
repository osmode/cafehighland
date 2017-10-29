var port = chrome.extension.connect({name:'test'});

document.getElementById("theButton").addEventListener("click", function() {

    port.postMessage({action:"getNetworkLog"});

}, false);

port.onMessage.addListener(function(msg) {
  document.getElementById('outputDiv').innerHTML = JSON.stringify(msg);
});

