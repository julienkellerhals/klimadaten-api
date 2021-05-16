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
