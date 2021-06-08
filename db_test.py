import db
import pytest
import sqlalchemy
import pandas as pd
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

    # Test if database engine exists and is of right type
    def testGetEngineSuccess(self):
        engine = instance.getEngine()
        assert type(engine) == sqlalchemy.engine.base.Engine

    # Test if refresh dates are in a dataframe
    # and dataframe has at least one entry
    def testGetParameterRefreshDateSuccess(self):
        table = instance.getParameterRefreshDate()
        if type(table) == pd.core.frame.DataFrame:
            assert len(table) > 0
        else:
            assert False

    # Test if the refresh dates table has the necessary columns
    def testGetParameterRefreshDateColumns(self):
        table = instance.getParameterRefreshDate()
        assert 'meas_name' and 'valid_from' in table.columns
