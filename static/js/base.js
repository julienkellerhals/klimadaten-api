var refreshInterval = 20000
// TODO maybe remove these and add them on on message event

function postReq(url) {
    console.log(url)
    var xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.send()
    return xhr
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

function createLi(colName, title) {
    var li = document.createElement("li")
    li.id = camelize(colName + " " + title)
    return li
}

function createHeaderDiv() {
    var headerDiv = document.createElement("div")
    headerDiv.classList.add("collapsible-header")
    return headerDiv
}

function createHeaderTitle(headerDiv, title) {
    var title = document.createTextNode(title)
    headerDiv.appendChild(title)
    return headerDiv
}

function createHeaderBadge(headerDiv, caption, content) {
    var headerBadge = document.createElement("span")
    headerBadge.classList.add("badge")
    var badgeAttribute = document.createAttribute("data-badge-caption")
    badgeAttribute.value = caption
    headerBadge.setAttributeNode(badgeAttribute)
    headerBadge.innerHTML = content
    headerDiv.appendChild(headerBadge)
    return headerDiv
}

function createBodyDiv() {
    var bodyDiv = document.createElement("div")
    bodyDiv.classList.add("collapsible-body")
    return bodyDiv
}

function createActionRow() {
    var actionRow = document.createElement("div")
    actionRow.classList.add("row")
    return actionRow
}

function createActionButton(name, enabled) {
    var actionButton = document.createElement("a")
    actionButton.classList.add("waves-effect")
    actionButton.classList.add("waves-light")
    actionButton.classList.add("btn-small")
    actionButton.innerHTML = name
    if (enabled == true) {
        actionButton.classList.remove("disabled")
    } else {
        actionButton.classList.add("disabled")
    }
    return actionButton
}

function appendAction(bodyDiv, actionRow, actionButton) {
    actionRow.appendChild(actionButton)
    bodyDiv.appendChild(actionRow)
    return bodyDiv
}

function createBodyBadgeRow() {
    var bodyBadgeRow = document.createElement("div")
    bodyBadgeRow.classList.add("row")
    return bodyBadgeRow
}

function createBodyBadge(caption, content) {
    if (content != null) {
        var bodyBadge = document.createElement("span")
        bodyBadge.classList.add("badge")
        var badgeAttribute = document.createAttribute("data-badge-caption")
        badgeAttribute.value = caption
        bodyBadge.setAttributeNode(badgeAttribute)
        bodyBadge.innerHTML = content
    } else {
        var bodyBadge = document.createElement("span")
        bodyBadge.classList.add("badge")
        var badgeAttribute = document.createAttribute("data-badge-caption")
        badgeAttribute.value = ""
        bodyBadge.setAttributeNode(badgeAttribute)
        bodyBadge.innerHTML = ""
    }
    return bodyBadge
}

function appendBodyBadge(bodyDiv, bodyBadgeRow, bodyBadge) {
    bodyBadgeRow.appendChild(bodyBadge)
    bodyDiv.appendChild(bodyBadgeRow)
    return bodyDiv
}

function appendLi(ul, li, headerDiv, bodyDiv) {
    li.appendChild(headerDiv)
    li.appendChild(bodyDiv)
    ul.appendChild(li)
}

function createRowStructure(row, colName, ul) {
    var li = createLi(colName, row.title)

    var headerDiv = createHeaderDiv()
    headerDiv = createHeaderTitle(headerDiv, row.title)
    headerDiv = createHeaderBadge(headerDiv, row.headerBadge.caption, row.headerBadge.content)

    var bodyDiv = createBodyDiv()

    row.action.forEach(action => {
        var actionRow = createActionRow()
        var actionButton = createActionButton(action.name, action.enabled)
        bodyDiv = appendAction(bodyDiv, actionRow, actionButton)
    })

    var bodyBadgeRow = createBodyBadgeRow()
    var bodyBadge = createBodyBadge(row.bodyBadge.caption, row.bodyBadge.content)
    bodyDiv = appendBodyBadge(bodyDiv, bodyBadgeRow, bodyBadge)

    appendLi(ul, li, headerDiv, bodyDiv)
}

function updateRowStructure(content, previousContent, colName, ul) {
    // TODO Update still not working
    // Use table trigger maybe
    var row = document.getElementById(camelize(colName + " " + content.title))
    if (row == null) {
        createRowStructure(content, colName, ul)
        var row = document.getElementById(camelize(colName + " " + content.title))
    }
    var contentDiff = diff(previousContent, content)
    console.log(content)
    console.log(previousContent)
    console.log(contentDiff)
    // FIXME None check may not work
    if (contentDiff != null) {
        if (contentDiff.title != undefined) {
            row.querySelector("div.collapsible-header").childNodes[0].nodeValue = contentDiff.title
        }
        if (contentDiff.headerBadge.caption != undefined) {
            row.querySelector("div.collapsible-header > span").attributes["data-badge-caption"].value = contentDiff.headerBadge.caption
        }
        if (contentDiff.headerBadge.content != undefined) {
            row.querySelector("div.collapsible-header > span").innerHTML = contentDiff.headerBadge.content
        }
        if (contentDiff.action != undefined) {
            Object.keys(contentDiff.action).forEach((idx) => {
                var nthChild = String(parseInt(idx) + 1)
                if (contentDiff.action[idx].name != undefined) {
                    row.querySelector("div.collapsible-body > div:nth-child(" + nthChild + ") > a").innerText = contentDiff.action[idx].name
                }
                if (contentDiff.action[idx].actionUrl != undefined) {
                    row.querySelector("div.collapsible-body > div:nth-child(" + nthChild + ") > a").addEventListener(
                        "mouseup",
                        () => {
                            // event.stopPropagation()
                            postReq(contentDiff.action[idx].actionUrl)
                        }
                    )
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
}

function createCollapsibleElements(baseStructure) {
    const keys = Object.keys(baseStructure)
    keys.forEach((id) => {
        const ul = document.getElementById(id)
        var previousContent = undefined
        var previousProgressBar = false

        if (baseStructure[id].eventSourceUrl != undefined) {
            var colEventSourceUrl = baseStructure[id].eventSourceUrl
            var colEventSource = new EventSource(colEventSourceUrl)

            var rows = Object.keys(baseStructure[id]).filter((r) => r.endsWith("_t")).sort()
            rows.forEach((rowName) => {
                var row = baseStructure[id][rowName]
                createRowStructure(row, id, ul)
            })

            delete baseStructure[id].eventSourceUrl
            previousContent = baseStructure[id]

            colEventSource.onmessage = function (e) {
                var content = JSON.parse(e.data);
                if (content[id].progressBar == true && previousProgressBar == false) {
                    var progress = document.createElement("div")
                    progress.classList.add("progress")
                    var progressBar = document.createElement("div")
                    progressBar.classList.add("indeterminate")
                    progress.appendChild(progressBar)

                    ul.parentNode.insertBefore(progress, ul.parentNode.children[1])
                    previousProgressBar = true
                } else if (content[id].progressBar == false && previousProgressBar == true) {
                    ul.parentNode.children[1].remove()
                    previousProgressBar = false
                }

                var rows = Object.keys(content[id]).filter((r) => r.endsWith("_t")).sort()
                rows.forEach((rowName) => {
                    var row = content[id][rowName]
                    try {
                        updateRowStructure(row, previousContent[id][rowName], id, ul)
                    } catch (error) {
                        updateRowStructure(row, {}, id, ul)
                    }
                })
                previousContent = content
            }
        } else {
            var rows = Object.keys(baseStructure[id]).sort()
            rows.forEach((rowName) => {
                var row = baseStructure[id][rowName]
                createRowStructure(row, id, ul)
                if (row.eventSourceUrl != undefined) {
                    var rowEventSource = new EventSource(row.eventSourceUrl);
                    rowEventSource.onmessage = function (e) {
                        var content = JSON.parse(e.data)
                        try {
                            updateRowStructure(content, previousContent[id][rowName], id, ul)
                        } catch (error) {
                            updateRowStructure(content, {}, id, ul)
                        }
                        if (previousContent == undefined) {
                            previousContent = {}
                        }
                        if (previousContent[id] == undefined) {
                            previousContent[id] = {}
                        }
                        if (previousContent[id][rowName] == undefined) {
                            previousContent[id][rowName] = {}
                        }
                        previousContent[id][rowName] = content
                    }
                }
            })
        }
    })
}
