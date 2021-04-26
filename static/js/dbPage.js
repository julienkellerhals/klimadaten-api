class RunETL {
    constructor(divId) {
        this.div = document.getElementById(divId)
    }
    req(url) {
        // progress bar
        var progress = document.createElement("div")
        progress.classList.add("progress")
        var progressBar = document.createElement("div")
        progressBar.classList.add("indeterminate")
        progress.appendChild(progressBar)
        this.div.insertBefore(progress, this.div.children[1])

        // disable buttons
        var anchorlist = this.div.getElementsByTagName("a")
        Array.from(anchorlist).forEach(anchor => {
            anchor.classList.add("disabled")
        })

        // send requests
        var xhr = new XMLHttpRequest();
        xhr.onload = () => {
            div.children[1].remove()
            Array.from(anchorlist).forEach(anchor => {
                anchor.classList.remove("disabled")
            })
        }
        xhr.open("POST", url, true);
        xhr.send()
    }
}

function runScrapping(tableName) {
    var url = "/admin/scrape/" + tableName.replaceAll("_t", "")
    stageETL.req(url)
}
function runInitialLoad(tableName) {
    var url = "/admin/db/etl/stage/" + tableName.replaceAll("_t", "")
    stageETL.req(url)
}
function runIncrementLoad(tableName) {
    var url = "/admin/db/etl/stage/increment/" + tableName.replaceAll("_t", "")
    stageETL.req(url)
}
function load(tableName) {
    var url = "/admin/db/etl/core/" + tableName.replaceAll("_t", "")
    coreETL.req(url)
}

// Other getStatus set in base
setInterval(getStatus("/admin/getTablesStatus"), refreshInterval)


var currentStatus = null
function checkStatus() {
    if (currentStatus == "tbCreate") {
        document.getElementById("dbAction").classList.add("disabled")
    }
}
function execCurrentAction() {
    if (currentStatus == null) {
        runAction("/admin/db/connect", "/admin/getEngineStatus")
    } else if (currentStatus == "dbConnection") {
        runAction("/admin/db/create", "/admin/getDatabaseStatus")
    } else if (currentStatus == "dbCreate") {
        runAction("/admin/db/table", "/admin/getTablesStatus")
    }
}

function runAction(actionUrl, statusUrl) {
    document.getElementById("dbAction").classList.add("disabled")
    var xhr = new XMLHttpRequest();
    xhr.onload = () => {
        document.getElementById("dbAction").classList.remove("disabled")
    }
    xhr.open("POST", actionUrl, true);
    xhr.send()
    getStatus(statusUrl)
}

M.AutoInit();
var stageETL = new RunETL("stage")
var coreETL = new RunETL("core")
var datamartETL = new RunETL("datamart")

function streamEngineStatus() {
    var engineEventSource = new EventSource("/admin/stream/getEngineStatus");
    var previousStatusCode = null
    engineEventSource.onmessage = function (e) {
        var content = e.data
        var statusCode = parseInt(content.split(";")[0].split(":")[1]);
        var dbConnection = document.getElementById("dbConnection")
        if (previousStatusCode != statusCode || currentStatus == "null") {
            previousStatusCode = statusCode
            if (statusCode == 1) {
                document.getElementById("dbAction").classList.remove("disabled")
                dbConnection.classList.remove("text-darken-1")
                dbConnection.classList.add("text-lighten-5")
                currentStatus = null
            } else if (statusCode == 0) {
                dbConnection.classList.remove("text-lighten-5")
                dbConnection.classList.add("text-darken-1")
                currentStatus = "dbConnection"
            }
        }
        checkStatus()
    }
}

function streamDatabaseStatus() {
    var databaseEventSource = new EventSource("/admin/stream/getDatabaseStatus");
    var previousStatusCode = null
    databaseEventSource.onmessage = function (e) {
        var content = e.data;
        var statusCode = parseInt(content.split(";")[0].split(":")[1]);
        var dbCreate = document.getElementById("dbCreate")
        if (previousStatusCode != statusCode || currentStatus == "dbConnection") {
            previousStatusCode = statusCode
            if (statusCode == 0) {
                // msgTxt = "Status: 0; Database connection: " + str(self.databaseUrl)
                dbCreate.classList.remove("text-lighten-5")
                dbCreate.classList.add("text-darken-1")
                if (currentStatus == null) {
                    currentStatus = null
                } else if (currentStatus == "dbConnection") {
                    currentStatus = "dbCreate"
                }
            } else if (statusCode == 1) {
                // msgTxt = "Status: 1; Database not created; Error: " + str(e)
                document.getElementById("dbAction").classList.remove("disabled")
                dbCreate.classList.remove("text-darken-1")
                dbCreate.classList.add("text-lighten-5")
                if (currentStatus == null) {
                    currentStatus = null
                } else if (currentStatus == "dbConnection") {
                    currentStatus = "dbConnection"
                } else if (currentStatus == "dbCreate") {
                    currentStatus = null
                }
            } else if (statusCode == 2) {
                // msgTxt = "Status: 2; Database not started; Error: " + str(e)
                document.getElementById("dbAction").classList.remove("disabled")
                dbCreate.classList.remove("text-darken-1")
                dbCreate.classList.add("text-lighten-5")
                if (currentStatus == null) {
                    currentStatus = null
                } else if (currentStatus == "dbConnection") {
                    currentStatus = "dbConnection"
                } else if (currentStatus == "dbCreate") {
                    currentStatus = null
                }
            }
        }
        checkStatus()
    }
}

function streamTablesStatus() {
    var tablesEventSource = new EventSource("/admin/stream/getTablesStatus");
    var previousStatusCode = null
    var previousMessage = null
    tablesEventSource.onmessage = function (e) {
        var content = e.data;
        var statusCode = parseInt(content.split(";")[0].split(":")[1]);
        var message = content.split(";")[1]
        var tbCreate = document.getElementById("tbCreate")
        if (previousStatusCode != statusCode || previousMessage != message || currentStatus == "dbCreate") {
            previousStatusCode = statusCode
            previousMessage = message
            if (statusCode == 0) {
                var tablesJson = JSON.parse(message)

                document.getElementById("stageTableGroup").innerHTML = ""
                document.getElementById("coreTableGroup").innerHTML = ""

                tablesJson.stage.forEach(element => {
                    var li = document.createElement("li")

                    var headerDiv = document.createElement("div")
                    headerDiv.classList.add("collapsible-header")
                    var headerTitle = document.createTextNode(element.name)
                    headerDiv.appendChild(headerTitle)
                    headerDiv.insertAdjacentHTML("beforeend", "<span class='badge' data-badge-caption='rows'>" + element.nrow.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,') + "</span>")

                    var bodyDiv = document.createElement("div")
                    bodyDiv.classList.add("collapsible-body")
                    element.action.forEach(action => {
                        if (action == "Run scrapping") {
                            bodyDiv.insertAdjacentHTML(
                                "beforeend",
                                "<div class='row'><a href='javascript:runScrapping(\"" + element.name + "\")' class='waves-effect waves-light btn-small'>" + action + "</a></div>"
                            )
                        } else if (action == "Initial load") {
                            bodyDiv.insertAdjacentHTML(
                                "beforeend",
                                "<div class='row'><a href='javascript:runInitialLoad(\"" + element.name + "\")' class='waves-effect waves-light btn-small " + action.replaceAll(" ", "") + "'>" + action + "</a></div>"
                            )
                        } else if (action == "Increment load") {
                            bodyDiv.insertAdjacentHTML(
                                "beforeend",
                                "<div class='row'><a href='javascript:runIncrementLoad(\"" + element.name + "\")' class='waves-effect waves-light btn-small " + action.replaceAll(" ", "") + "'>" + action + "</a></div>"
                            )
                        }
                    })
                    if (element.lastRefresh != null) {
                        bodyDiv.insertAdjacentHTML("beforeend", "<div class='row'><span class='badge' data-badge-caption='last refresh'>" + element.lastRefresh + "</span></div>")
                    }

                    li.appendChild(headerDiv)
                    li.appendChild(bodyDiv)
                    document.getElementById("stageTableGroup").appendChild(li)
                });

                tablesJson.core.forEach(element => {
                    var li = document.createElement("li")

                    var headerDiv = document.createElement("div")
                    headerDiv.classList.add("collapsible-header")
                    var headerTitle = document.createTextNode(element.name)
                    headerDiv.appendChild(headerTitle)
                    headerDiv.insertAdjacentHTML("beforeend", "<span class='badge' data-badge-caption='rows'>" + element.nrow.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,') + "</span>")

                    var bodyDiv = document.createElement("div")
                    bodyDiv.classList.add("collapsible-body")
                    element.action.forEach(action => {
                        if (action == "Load") {
                            bodyDiv.insertAdjacentHTML(
                                "beforeend",
                                "<div class='row'><a href='javascript:load(\"" + element.name + "\")' class='waves-effect waves-light btn-small'>" + action + "</a></div>"
                            )
                        }
                    })
                    if (element.lastRefresh != null) {
                        bodyDiv.insertAdjacentHTML("beforeend", "<div class='row'><span class='badge' data-badge-caption='last refresh'>" + element.lastRefresh + "</span></div>")
                    }

                    li.appendChild(headerDiv)
                    li.appendChild(bodyDiv)
                    document.getElementById("coreTableGroup").appendChild(li)
                });

                tbCreate.classList.remove("text-lighten-5")
                tbCreate.classList.add("text-darken-1")
                if (currentStatus == null) {
                    currentStatus = null
                } else if (currentStatus == "dbCreate") {
                    currentStatus = "tbCreate"
                }
            } else if (statusCode == 1) {
                document.getElementById("dbAction").classList.remove("disabled")
                tbCreate.classList.remove("text-darken-1")
                tbCreate.classList.add("text-lighten-5")
                if (currentStatus == null) {
                    currentStatus = null
                } else if (currentStatus == "dbConnection") {
                    currentStatus = "dbConnection"
                } else if (currentStatus == "tbCreate") {
                    currentStatus = null
                }
            }
        }
        checkStatus()
    }
}

streamEngineStatus()
streamDatabaseStatus()
streamTablesStatus()

document.getElementById("dbAction").addEventListener(
    "click",
    () => {
        execCurrentAction()
    }
)
document.getElementById("execScrapping").addEventListener(
    "click",
    () => {
        stageETL.req("/admin/scrape/")
    }
)
document.getElementById("execStageETL").addEventListener(
    "click",
    () => {
        stageETL.req("/admin/db/etl/stage")
    }
)
document.getElementById("execCoreETL").addEventListener(
    "click",
    () => {
        coreETL.req("/admin/db/etl/core")
    }
)
document.getElementById("execDatamartETL").addEventListener(
    "click",
    () => {
        datamartETL.req("/admin/db/etl/datamart")
    }
)
