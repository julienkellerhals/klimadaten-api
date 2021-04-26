M.AutoInit();

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

var serviceList = {
    "runningService": {
        "1": {
            "title": "Driver name",
            "url": "",
            "headerBadge": {
                "caption": "",
                "content": "",
            },
            "action": [
                {
                    "name": "Download driver",
                    "actionUrl": "",
                }
            ],
            "bodyBadge": {
                "caption": "",
                "content": "",
            },
        },
        "2": {
            "title": "Driver status",
            "url": "",
            "headerBadge": {
                "caption": "",
                "content": "",
            },
            "action": [
                {
                    "name": "Start driver",
                    "actionUrl": "",
                }
            ],
            "bodyBadge": {
                "caption": "",
                "content": "",
            },
        },
        "3": {
            "title": "Database connection",
            "url": "",
            "headerBadge": {
                "caption": "",
                "content": "",
            },
            "action": [
                {
                    "name": "Connect to db",
                    "actionUrl": "",
                }
            ],
            "bodyBadge": {
                "caption": "",
                "content": "",
            },
        },
        "4": {
            "title": "Engine status",
            "url": "",
            "headerBadge": {
                "caption": "",
                "content": "",
            },
            "action": [
                {
                    "name": "Start engine",
                    "actionUrl": "",
                    // "hrefScript": "javascript:runScrapping(\"" + element.name + "\")",
                }
            ],
            "bodyBadge": {
                "caption": "",
                "content": "",
            },
        },
    }
}

const keys = Object.keys(serviceList)
keys.forEach((id) => {
    const ul = document.getElementById(id)

    const rows = Object.keys(serviceList[id]).sort()

    rows.forEach((row) => {
        var row = serviceList[id][row]
        var li = document.createElement("li")

        var headerDiv = document.createElement("div")
        headerDiv.classList.add("collapsible-header")
        var title = document.createTextNode(row.title)
        headerDiv.appendChild(title)
        headerDiv.insertAdjacentHTML(
            "beforeend",
            "<span class='badge' data-badge-caption='" + row.headerBadge.caption +"'>" + row.headerBadge.content + "</span>"
        )

        var bodyDiv = document.createElement("div")
        bodyDiv.classList.add("collapsible-body")
        row.action.forEach(action => {
            bodyDiv.insertAdjacentHTML(
                "beforeend",
                "<div class='row'><a href='" + action.hrefScript + "' class='waves-effect waves-light btn-small'>" + action.name + "</a></div>"
            )
        })
        
        if (row.bodyBadge.content != null) {
            bodyDiv.insertAdjacentHTML(
                "beforeend",
                "<div class='row'><span class='badge' data-badge-caption='" + row.bodyBadge.caption +"'>" + row.bodyBadge.content + "</span></div>"
            )
        }

        li.appendChild(headerDiv)
        li.appendChild(bodyDiv)
        ul.appendChild(li)
    })
})

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
