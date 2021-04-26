// Other getStatus set in base
setInterval(getStatus("/admin/getDriverPathStatus"), refreshInterval)
setInterval(getStatus("/admin/getDriverStatus"), refreshInterval)

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

function streamDatabaseStatus() {
    var databaseEventSource = new EventSource("/admin/stream/getDatabaseStatus");
    var previousStatusCode = null
    databaseEventSource.onmessage = function (e) {
        var content = e.data;
        var statusCode = parseInt(content.split(";")[0].split(":")[1]);
        var msg = content.split(";")[1]
        var errorMsg = content.split(";")[2]
        var databaseStatusSpan = document.getElementById("databaseStatus").firstElementChild
        var databaseStatusDot = document.getElementById("databaseStatus").lastElementChild
        if (previousStatusCode != statusCode) {
            previousStatusCode = statusCode
            if (statusCode > 0) {
                databaseStatusSpan.innerText = msg.trim()
                databaseStatusDot.classList.remove("success")
                databaseStatusDot.classList.add("error")
                databaseStatusDot.title = errorMsg.trim()
            } else if (statusCode == 0) {
                databaseStatusSpan.innerText = msg.trim()
                databaseStatusDot.classList.remove("error")
                databaseStatusDot.classList.add("success")
                databaseStatusDot.title = ""
            }
        }
    };
}

function streamEngineStatus() {
    var engineEventSource = new EventSource("/admin/stream/getEngineStatus");
    var previousStatusCode = null
    engineEventSource.onmessage = function (e) {
        var content = e.data
        var statusCode = parseInt(content.split(";")[0].split(":")[1]);
        var msg = content.split(";")[1]
        var errorMsg = content.split(";")[2]
        var engineStatusSpan = document.getElementById("engineStatus").firstElementChild
        var engineStatusDot = document.getElementById("engineStatus").lastElementChild
        if (previousStatusCode != statusCode) {
            previousStatusCode = statusCode
            if (statusCode == 1) {
                engineStatusSpan.innerText = msg.trim()
                engineStatusDot.classList.remove("success")
                engineStatusDot.classList.add("error")
                engineStatusDot.title = errorMsg.trim()
            } else if (statusCode == 0) {
                engineStatusSpan.innerText = msg.trim()
                engineStatusDot.classList.remove("error")
                engineStatusDot.classList.add("success")
                engineStatusDot.title = ""
            }
        }
    };
}

function streamDriverPathStatus() {
    var driverPathEventSource = new EventSource("/admin/stream/getDriverPathStatus");
    var previousStatusCode = null
    driverPathEventSource.onmessage = function (e) {
        var content = e.data;
        var statusCode = parseInt(content.split(";")[0].split(":")[1]);
        var msg = content.split(";")[1]
        var driverLocSpan = document.getElementById("driverLoc").firstElementChild
        var driverLocDot = document.getElementById("driverLoc").lastElementChild
        if (previousStatusCode != statusCode) {
            previousStatusCode = statusCode
            if (statusCode == 1) {
                driverLocSpan.innerText = msg.trim()
                driverLocDot.classList.remove("success")
                driverLocDot.classList.add("error")
            } else if (statusCode == 0) {
                driverLocSpan.innerText = msg.trim()
                driverLocDot.classList.remove("error")
                driverLocDot.classList.add("success")
            }
        }
    };
}

function streamDriverStatus() {
    var driverEventSource = new EventSource("/admin/stream/getDriverStatus");
    var previousStatusCode = null
    driverEventSource.onmessage = function (e) {
        var content = e.data;
        var statusCode = parseInt(content.split(";")[0].split(":")[1]);
        var msg = content.split(";")[1]
        var errorMsg = content.split(";")[2]
        var driverStatusSpan = document.getElementById("driverStatus").firstElementChild
        var driverStatusDot = document.getElementById("driverStatus").lastElementChild
        if (previousStatusCode != statusCode) {
            previousStatusCode = statusCode
            if (statusCode == 1) {
                driverStatusSpan.innerText = "Webdriver " + msg.trim()
                driverStatusDot.classList.remove("success")
                driverStatusDot.classList.add("error")
                driverStatusDot.title = errorMsg.trim()
            } else if (statusCode == 0) {
                driverStatusSpan.innerText = "Webdriver " + msg.trim()
                driverStatusDot.classList.remove("error")
                driverStatusDot.classList.add("success")
                driverStatusDot.title = ""
            }
        }
    };
}

streamEventLog()
streamEngineStatus()
streamDatabaseStatus()
streamDriverPathStatus()
streamDriverStatus()
