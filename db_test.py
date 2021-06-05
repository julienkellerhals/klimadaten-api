import db
import pytest
import sqlalchemy
import messageAnnouncer
from typing import List

announcer = messageAnnouncer.MessageAnnouncer()
instance = db.Database(announcer)

# To run tests, type the following into the console:
# pytest -m database -s -v --color=yes


@pytest.mark.database
class TestDatabase():
    # Test if cofigfile exist with correct file
    def testReadConfigSuccess(self):
        configFileName = "idawebConfig.xml"
        configFile = instance.readConfig(configFileName)
        if isinstance(configFile, List):
            assert len(configFile) != 0
        else:
            assert False

    # Test if cofigfile exist with wrong file
    def testReadConfigFail(self):
        configFileName = "wrongFile.xml"
        configFile = instance.readConfig(configFileName)
        if isinstance(configFile, List):
            assert len(configFile) == 0
        else:
            assert False

    def testGetEngineSuccess(self):
        engine = instance.getEngine()
        assert type(engine) == sqlalchemy.engine.base.Engine
