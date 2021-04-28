M.AutoInit();

function streamEventLog() {
    var eventContainer = document.getElementById("eventLog");
    var eventSource = new EventSource("/admin/stream/eventLog")
    eventSource.onmessage = function (e) {
        var entry = document.createElement("div");
        entry.className = "eventItem"
        entry.innerHTML = e.data;
        eventContainer.appendChild(entry);
    }
}

setInterval( function() {
    postReq("/admin/getEngineStatus")
}
, refreshInterval)
setInterval( function() {
    postReq("/admin/getDatabaseStatus")
}
, refreshInterval)
setInterval( function() {
    postReq("/admin/getDriverPathStatus")
}, refreshInterval)
setInterval( function() {
    postReq("/admin/getDriverStatus")
}, refreshInterval)

var xhr = new XMLHttpRequest();
xhr.onload = () => {
    var serviceList = JSON.parse(xhr.response)
    createCollapsibleElements(serviceList)
}
xhr.open("POST", "/admin/getServiceList", true);
xhr.send()
