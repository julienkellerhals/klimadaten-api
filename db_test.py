import pytest
import messageAnnouncer
from typing import List
from db import Database


announcer = messageAnnouncer.MessageAnnouncer()
database = Database(announcer)


#pytest -v -m db

@pytest.mark.db
class DBTest():
    # Test if cofigfile exist with correct file
    def testReadConfigSuccess(self):
        configFileName = "idawebConfig.xml"
        configFile = database.readConfig(configFileName)
        if isinstance(configFile, List):
            assert len(configFile) != 0
        else:
            assert False

    # Test if cofigfile exist with wrong file
    def testReadConfigFail(self):
        configFileName = "wrongFile.xml"
        configFile = database.readConfig(configFileName)
        if isinstance(configFile, List):
            assert len(configFile) == 0
        else:
            assert False
