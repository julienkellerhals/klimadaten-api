import json


class ResponseDictionary:
    respDict = None
    statusStream = None

    def __init__(self, baseDict, statusStream):

        self.respDict = baseDict
        self.statusStream = statusStream

    def send(self):

        msgText = json.dumps(
            self.respDict,
            default=str
        )
        self.statusStream.announce(
            self.statusStream.format_sse(msgText)
        )

    def createProgressBar(self):
        raise NotImplementedError

    def removeProgressBar(self):
        raise NotImplementedError

    def disableAllButtons(self):

        schema = list(self.respDict.keys())[0]
        for table in self.respDict[schema].items():
            if type(table[1]) is dict:
                for index, _ in enumerate(table[1]["action"]):
                    self.respDict[
                        schema
                    ][
                        table[0]
                    ][
                        "action"
                    ][
                        index
                    ][
                        "enabled"
                    ] = False
        self.send()

    def enableAllButtons(self):

        schema = list(self.respDict.keys())[0]
        for table in self.respDict[schema].items():
            if type(table[1]) is dict:
                for index, _ in enumerate(table[1]["action"]):
                    self.respDict[
                        schema
                    ][
                        table[0]
                    ][
                        "action"
                    ][
                        index
                    ][
                        "enabled"
                    ] = True
        self.send()
