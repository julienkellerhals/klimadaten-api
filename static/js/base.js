var refreshInterval = 20000
// TODO maybe remove these and add them on on message event

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

function getStatus(url) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.send()
}

setInterval(getStatus("/admin/getEngineStatus"), refreshInterval)
setInterval(getStatus("/admin/getDatabaseStatus"), refreshInterval)

function createCollapsibleElements(baseStructure) {
    const keys = Object.keys(baseStructure)
    keys.forEach((id) => {
        const ul = document.getElementById(id)

        if (baseStructure[id].eventSourceUrl != undefined) {
            console.log("To be implemented")
            var colEventSourceUrl = baseStructure[id].eventSourceUrl
            var rows = Object.keys(baseStructure[id]).filter((r) => r != "eventSourceUrl").sort()
        } else {
            var rows = Object.keys(baseStructure[id]).sort()
        }

        rows.forEach((row) => {
            var row = baseStructure[id][row]
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
                            // FIXME Does not work with multiple actions
                            Object.keys(contentDiff.action).forEach((idx) => {
                                var nthChild = String(parseInt(idx)+1)
                                if (contentDiff.action[idx].name != undefined) {
                                    row.querySelector("div.collapsible-body > div:nth-child(" + nthChild + ") > a").innerText = contentDiff.action[idx].name
                                }
                                if (contentDiff.action[idx].actionUrl != undefined) {
                                    row.querySelector("div.collapsible-body > div:nth-child(" + nthChild + ") > a").href = contentDiff.action[idx].actionUrl
                                }
                                if (contentDiff.action[idx].enabled != undefined) {
                                    if (contentDiff.action[idx].enabled == false) {
                                        row.querySelector("div.collapsible-body > div:nth-child(" + nthChild + ") > a").classList.add("disabled")
                                    } else {
                                        row.querySelector("div.collapsible-body > div:nth-child(" + nthChild + ") > a").classList.remove("disabled")
                                    }
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

            var headerBadge = document.createElement("span")
            headerBadge.classList.add("badge")
            var badgeAttribute = document.createAttribute("data-badge-caption")
            badgeAttribute.value = row.headerBadge.caption
            headerBadge.setAttributeNode(badgeAttribute)
            headerBadge.innerHTML = row.headerBadge.content
            headerDiv.appendChild(headerBadge)

            var bodyDiv = document.createElement("div")
            bodyDiv.classList.add("collapsible-body")
            row.action.forEach(action => {
                // FIXME Does not work with multiple actions
                // disabled
                var actionRow = document.createElement("div")
                actionRow.classList.add("row")

                var actionButton = document.createElement("a")
                actionButton.href = action.actionUrl
                actionButton.classList.add("waves-effect")
                actionButton.classList.add("waves-light")
                actionButton.classList.add("btn-small")
                actionButton.innerHTML = action.name
                if (action.enabled == true) {
                    actionButton.classList.remove("disabled")
                } else {
                    actionButton.classList.add("disabled")
                }
                actionRow.appendChild(actionButton)
                bodyDiv.appendChild(actionRow)
            })

            if (row.bodyBadge.content != null) {    
                var bodyBadgeRow = document.createElement("div")
                bodyBadgeRow.classList.add("row")
            
                var bodyBadge = document.createElement("span")
                bodyBadge.classList.add("badge")
                var badgeAttribute = document.createAttribute("data-badge-caption")
                badgeAttribute.value = row.bodyBadge.caption
                bodyBadge.setAttributeNode(badgeAttribute)
                bodyBadge.innerHTML = row.bodyBadge.content

                bodyBadgeRow.appendChild(bodyBadge)
                bodyDiv.appendChild(bodyBadgeRow)
            }

            li.appendChild(headerDiv)
            li.appendChild(bodyDiv)
            ul.appendChild(li)
        })
    })
}
