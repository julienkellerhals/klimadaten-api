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

// Other getStatus set in base
setInterval(getStatus("/admin/getDriverPathStatus"), refreshInterval)
setInterval(getStatus("/admin/getDriverStatus"), refreshInterval)

var xhr = new XMLHttpRequest();
xhr.onload = () => {
    var serviceList = JSON.parse(xhr.response)
    createCollapsibleElements(serviceList)
}
xhr.open("POST", "/admin/getServiceList", true);
xhr.send()
