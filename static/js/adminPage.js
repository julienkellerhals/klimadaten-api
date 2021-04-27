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
        // "eventSourceUrl": "",
        "1": {
            "eventSourceUrl": "/admin/stream/getDriverPathStatus",
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
            "eventSourceUrl": "/admin/stream/getDriverStatus",
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
            "eventSourceUrl": "/admin/stream/getDatabaseStatus",
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
            "eventSourceUrl": "/admin/stream/getEngineStatus",
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

function camelize(str) {
    return str.toLowerCase().replace(/[^a-zA-Z0-9]+(.)/g, (m, chr) => chr.toUpperCase());
}

function diff(obj1, obj2) {
    const result = {};
    if (Object.is(obj1, obj2)) {
        return undefined;
    }
    if (!obj2 || typeof obj2 !== 'object') {
        return obj2;
    }
    Object.keys(obj1 || {}).concat(Object.keys(obj2 || {})).forEach(key => {
        if (obj2[key] !== obj1[key] && !Object.is(obj1[key], obj2[key])) {
            result[key] = obj2[key];
        }
        if (typeof obj2[key] === 'object' && typeof obj1[key] === 'object') {
            const value = diff(obj1[key], obj2[key]);
            if (value !== undefined) {
                result[key] = value;
            }
        }
    });
    return result;
}

const keys = Object.keys(serviceList)
keys.forEach((id) => {
    const ul = document.getElementById(id)

    if (serviceList[id].eventSourceUrl != undefined) {
        console.log("To be implemented")
        var colEventSourceUrl = serviceList[id].eventSourceUrl
        var rows = Object.keys(serviceList[id]).filter((r) => r != "eventSourceUrl").sort()
    } else {
        var rows = Object.keys(serviceList[id]).sort()
    }

    rows.forEach((row) => {
        var row = serviceList[id][row]
        var li = document.createElement("li")
        li.id = camelize(row.title)

        if (row.eventSourceUrl != undefined) {
            var rowEventSource = new EventSource(row.eventSourceUrl);
            var previousContent = row
            rowEventSource.onmessage = function (e) {
                var content = JSON.parse(e.data);
                var row = document.getElementById(camelize(content.title))
                var contentDiff = diff(previousContent, content)
                if (contentDiff != null) {
                    if (contentDiff.title != undefined) {
                        row.querySelector("div.collapsible-header").innerText = contentDiff.title
                    }
                    if (contentDiff.headerBadge.caption != undefined) {
                        row.querySelector("div.collapsible-header > span").attributes["data-badge-caption"].value = contentDiff.headerBadge.caption
                    }
                    if (contentDiff.headerBadge.content != undefined) {
                        row.querySelector("div.collapsible-header > span").innerHTML = contentDiff.headerBadge.content
                    }
                    if (contentDiff.action != undefined) {
                        Array(contentDiff.action).forEach((a) => {
                            if (a.name != undefined) {
                                row.querySelector("div.collapsible-body > div:nth-child(1) > a").innerText = a.name
                            }
                            if (a.actionUrl != undefined) {
                                row.querySelector("div.collapsible-body > div:nth-child(1) > a").href = a.actionUrl
                            }
                        })
                    }
                    if (contentDiff.bodyBadge.caption != undefined) {
                        row.querySelector("div.collapsible-body > div:last-child > span").attributes["data-badge-caption"].value = contentDiff.bodyBadge.caption
                    }
                    if (contentDiff.bodyBadge.content != undefined) {
                        row.querySelector("div.collapsible-body > div:last-child > span").innerHTML = contentDiff.bodyBadge.content
                    }
                    previousContent = content
                }
            };
        }

        var headerDiv = document.createElement("div")
        headerDiv.classList.add("collapsible-header")
        var title = document.createTextNode(row.title)
        headerDiv.appendChild(title)
        headerDiv.insertAdjacentHTML(
            "beforeend",
            "<span class='badge' data-badge-caption='" + row.headerBadge.caption + "'>" + row.headerBadge.content + "</span>"
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
                "<div class='row'><span class='badge' data-badge-caption='" + row.bodyBadge.caption + "'>" + row.bodyBadge.content + "</span></div>"
            )
        }

        li.appendChild(headerDiv)
        li.appendChild(bodyDiv)
        ul.appendChild(li)
    })
})
