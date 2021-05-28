import json


class ResponseDictionary:
    respDict = None
    statusStream = None
    schema = None

    def __init__(self, baseDict, statusStream):

        self.respDict = baseDict
        self.statusStream = statusStream
        self.schema = list(self.respDict.keys())[0]

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

    def endLoadProcess(self):

        self.enableAllButtons()
        self.removeProgressBar()
        self.send()

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

    def updateRowCount(self):
        raise NotImplementedError
        # Do not forget to exec send after launching this function
