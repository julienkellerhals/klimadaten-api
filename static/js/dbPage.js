M.AutoInit();

var xhr = new XMLHttpRequest();
xhr.onload = () => {
    var serviceList = JSON.parse(xhr.response)
    updateBreadcrumbNav(serviceList)
}
xhr.open("POST", "/admin/getDbServiceList", true);
xhr.send()

setInterval( function() {
    postReq("/admin/getDbServiceStatus")
}, refreshInterval)

function createTableLists() {
    // Horrible hack but it works
    createTableLists = function(){}
    var xhr = new XMLHttpRequest();
    xhr.onload = () => {
        var tableStruct = JSON.parse(xhr.response)
        createCollapsibleElements(tableStruct)
    }
    xhr.open("POST", "/admin/getTablesList", true);
    xhr.send()
}

function updateBreadcrumbNav(serviceList) {
    var navEventSource = new EventSource(serviceList.runningService.eventSourceUrl)
    var previousContent = serviceList
    document.getElementById("dbAction").classList.add("disabled")
    navEventSource.onmessage = function (e) {
        var content = JSON.parse(e.data)
        if (content.runningService.tbCreate.dbReady == true) {
            createTableLists()
        }
        var contentDiff = diff(previousContent, content)
        if (Object.keys(contentDiff.runningService).length > 0) {
            if (Object.keys(contentDiff.runningService.dbConnection).length > 0) {
                if (contentDiff.runningService.dbConnection.currentAction != undefined) {
                    var dbConnection = document.getElementById("dbConnection")
                    if (contentDiff.runningService.dbConnection.currentAction == true) {
                        dbConnection.classList.remove("text-darken-1")
                        dbConnection.classList.add("text-lighten-5")
                    } else {
                        dbConnection.classList.remove("text-lighten-5")
                        dbConnection.classList.add("text-darken-1")
                    }
                }

                if (contentDiff.runningService.dbConnection.actionUrl != undefined) {
                    document.getElementById("dbAction").classList.remove("disabled")
                    document.getElementById("dbAction").addEventListener(
                        "mouseup",
                        () => {
                            document.getElementById("dbAction").classList.add("disabled")
                            var actionReq = postReq(contentDiff.runningService.dbConnection.actionUrl)
                            actionReq.onload = () => {
                                postReq("/admin/getDbServiceStatus")
                            }
                        },
                        {
                            once: true
                        }
                    )
                }
                previousContent.runningService.dbConnection = content.runningService.dbConnection
            }
            if (Object.keys(contentDiff.runningService.dbCreate).length > 0) {
                if (contentDiff.runningService.dbCreate.currentAction != undefined) {
                    var dbCreate = document.getElementById("dbCreate")
                    if (contentDiff.runningService.dbCreate.currentAction == true) {
                        dbCreate.classList.remove("text-darken-1")
                        dbCreate.classList.add("text-lighten-5")
                    } else {
                        dbCreate.classList.remove("text-lighten-5")
                        dbCreate.classList.add("text-darken-1")
                    }
                }

                if (contentDiff.runningService.dbCreate.actionUrl != undefined) {
                    document.getElementById("dbAction").classList.remove("disabled")
                    document.getElementById("dbAction").addEventListener(
                        "mouseup",
                        () => {
                            document.getElementById("dbAction").classList.add("disabled")
                            var actionReq = postReq(contentDiff.runningService.dbCreate.actionUrl)
                            actionReq.onload = () => {
                                postReq("/admin/getDbServiceStatus")
                            }
                        },
                        {
                            once: true
                        }
                    )
                }
                previousContent.runningService.dbCreate = content.runningService.dbCreate
            }
            if (Object.keys(contentDiff.runningService.tbCreate).length > 0) {
                if (contentDiff.runningService.tbCreate.currentAction != undefined) {
                    var tbCreate = document.getElementById("tbCreate")
                    if (contentDiff.runningService.tbCreate.currentAction == true) {
                        tbCreate.classList.remove("text-darken-1")
                        tbCreate.classList.add("text-lighten-5")
                    } else {
                        tbCreate.classList.remove("text-lighten-5")
                        tbCreate.classList.add("text-darken-1")
                    }
                }

                if (contentDiff.runningService.tbCreate.actionUrl != undefined) {
                    document.getElementById("dbAction").classList.remove("disabled")
                    document.getElementById("dbAction").addEventListener(
                        "mouseup",
                        () => {
                            document.getElementById("dbAction").classList.add("disabled")
                            var actionReq = postReq(contentDiff.runningService.tbCreate.actionUrl)
                            actionReq.onload = () => {
                                postReq("/admin/getDbServiceStatus")
                            }
                        },
                        {
                            once: true
                        }
                    )
                }
                previousContent.runningService.tbCreate = content.runningService.tbCreate
            }
        }
    }
}
