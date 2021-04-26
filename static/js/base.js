var refreshInterval = 20000
// TODO maybe remove these and add them on on message event

function getStatus(url) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.send()
}

setInterval(getStatus("/admin/getEngineStatus"), refreshInterval)
setInterval(getStatus("/admin/getDatabaseStatus"), refreshInterval)