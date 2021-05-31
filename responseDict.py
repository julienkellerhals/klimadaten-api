import json


class ResponseDictionary:
    respDict = None
    statusStream = None
    schema = None
    instance = None

    def __init__(self, baseDict, statusStream, instance):

        self.respDict = baseDict
        self.statusStream = statusStream
        self.schema = list(self.respDict.keys())[0]
        self.instance = instance

    def send(self):

        msgText = json.dumps(
            self.respDict,
            default=str
        )
        self.statusStream.announce(
            self.statusStream.format_sse(msgText)
        )

    def startLoadProcess(self):

        self.disableAllButtons()
        self.createProgressBar()
        self.send()
        self.refreshMV()
        self.updateDictRowCount()
        self.updateDictLastRefresh()
        self.send()

    def updateLoadProcess(self):
        self.refreshMV()
        self.updateDictRowCount()
        self.updateDictLastRefresh()
        self.send()

    def endLoadProcess(self):

        self.enableAllButtons()
        self.removeProgressBar()
        self.send()
        self.refreshMV()
        self.updateDictRowCount()
        self.updateDictLastRefresh()
        self.send()

    def refreshMV(self):

        engine = self.instance.getEngine()
        for table in self.respDict[self.schema].items():
            if type(table[1]) is dict:
                engine.execute(
                    "REFRESH MATERIALIZED VIEW {}.{}_count_mv".format(
                        self.schema,
                        table[0].strip("_t")
                    )
                )
                engine.execute(
                    "REFRESH MATERIALIZED VIEW {}.{}_max_valid_from_mv".format(
                        self.schema,
                        table[0].strip("_t")
                    )
                )

    def createProgressBar(self):

        self.respDict[self.schema]["progressBar"] = True

    def removeProgressBar(self):

        self.respDict[self.schema]["progressBar"] = False

    def disableAllButtons(self):

        for table in self.respDict[self.schema].items():
            if type(table[1]) is dict:
                for index, _ in enumerate(table[1]["action"]):
                    self.respDict[
                        self.schema
                    ][
                        table[0]
                    ][
                        "action"
                    ][
                        index
                    ][
                        "enabled"
                    ] = False
            if type(table[1]) is list:
                for action in table[1]:
                    action["enabled"] = False

    def enableAllButtons(self):

        for table in self.respDict[self.schema].items():
            if type(table[1]) is dict:
                for index, _ in enumerate(table[1]["action"]):
                    self.respDict[
                        self.schema
                    ][
                        table[0]
                    ][
                        "action"
                    ][
                        index
                    ][
                        "enabled"
                    ] = True
            if type(table[1]) is list:
                for action in table[1]:
                    action["enabled"] = True

    def updateDictRowCount(self):

        engine = self.instance.getEngine()
        for table in self.respDict[self.schema].items():
            if type(table[1]) is dict:
                nrowQuery = "SELECT * FROM {}.{}_count_mv".format(
                    self.schema,
                    table[0].strip("_t")
                )
                table[1]["headerBadge"]["content"] = \
                    "{:,}".format(engine.execute(
                        nrowQuery
                    ).first()[0])

    def updateDictLastRefresh(self):

        engine = self.instance.getEngine()
        for table in self.respDict[self.schema].items():
            if type(table[1]) is dict:
                lastRefreshQuery = \
                    "SELECT * FROM {}.{}_max_valid_from_mv".format(
                        self.schema,
                        table[0].strip("_t")
                    )

                table[1]["bodyBadge"] = {}
                lastRefresh = engine.execute(
                    lastRefreshQuery
                ).first()[0]
                if lastRefresh is not None:
                    table[1]["bodyBadge"]["caption"] = \
                        "last refresh"
                    table[1]["bodyBadge"]["content"] = \
                        lastRefresh
