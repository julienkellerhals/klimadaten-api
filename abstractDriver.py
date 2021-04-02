import os
import io
import zipfile
import threading
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.command import Command
from selenium.common.exceptions import WebDriverException
from msedge.selenium_tools import EdgeOptions
from msedge.selenium_tools import Edge
import download
import messageAnnouncer


class AbstractDriver():
    driver = None
    browser = None
    driverPath = None
    driverFolder = Path.cwd() / "driver"
    driverInstalledBool = False
    headless = False
    userAgent = None
    announcer = None
    pathStatusStream = None
    driverStatusStream = None

    def __init__(self, announcer):
        self.pathStatusStream = messageAnnouncer.MessageAnnouncer()
        self.driverStatusStream = messageAnnouncer.MessageAnnouncer()
        self.announcer = announcer

    def getDriverPathStatus(self):
        x = threading.Thread(
            target=self._getDriverPathStatus
        )
        x.start()

    def _getDriverPathStatus(self):
        if self.driverPath is None:
            self.getDriverPath(self.driverFolder, None)
            if self.driverInstalledBool is False:
                msgTxt = "Status: 1; Error: Driver not installed"
                self.pathStatusStream.announce(
                    self.pathStatusStream.format_sse(msgTxt)
                )
            else:
                msgTxt = "Status: 0; Driver: " + str(self.driverPath.stem)
                self.pathStatusStream.announce(
                    self.pathStatusStream.format_sse(msgTxt)
                )
        else:
            msgTxt = "Status: 0; Driver: " + str(self.driverPath.stem)
            self.pathStatusStream.announce(
                self.pathStatusStream.format_sse(msgTxt)
            )

    def getDriverStatus(self):
        x = threading.Thread(
            target=self._getDriverStatus
        )
        x.start()

    def _getDriverStatus(self):
        try:
            self.driver.window_handles
        except WebDriverException as e:
            msgTxt = "Status: 1; not started; Error: " + str(e)
            self.driverStatusStream.announce(
                self.driverStatusStream.format_sse(msgTxt)
            )
        except AttributeError as e:
            msgTxt = "Status: 1; not started; Error: " + str(e)
            self.driverStatusStream.announce(
                self.driverStatusStream.format_sse(msgTxt)
            )
        else:
            msgTxt = "Status: 0; instance: " \
                + str(self.driver.window_handles[0])
            self.driverStatusStream.announce(
                self.driverStatusStream.format_sse(msgTxt)
            )

    def checkDriver(self):
        if self.driver is None:
            print("Driver not started")
            print("Starting programatically")
            print("Assuming you installed only required drivers")
            _, self.driverPath = self.getDriverPath(self.driverFolder, None)
            if self.driverPath.name == "msedgedriver.exe":
                self.browser = "Edg"
            elif driverPath.name == "chromedriver.exe":
                self.browser = "Chrome"
            else:
                print("Browser not supported yet")
            # make browser headless or not
            self.createDriver(self.browser, self.driverPath, False)
        else:
            try:
                self.driver.execute(Command.STATUS)
            except:
                self.createDriver(self.browser, self.driverPath, False)

    def getDriver(self):
        self.checkDriver()
        return self.driver

    def getDriverPath(self, driverFolder, browser=None):
        """ Check if driver is installed and returns path

        Args:
            driverFolder (Path): Pathlib path to driver folder
            browser (string, optional): Browser type. Defaults to None.

        Returns:
            driverInstalledBool (bool): True if driver was found
            driverPath (Path): Driver + driver name path
        """

        for driverPath in list(driverFolder.glob('**/*.exe')):
            if browser is not None:
                if browser.lower() in driverPath.name:
                    self.driverInstalledBool = True
                    self.driverPath = driverPath
            else:
                self.driverInstalledBool = True
                self.driverPath = driverPath
        return self.driverInstalledBool, self.driverPath

    def downloadDriver(self, browser, headlessStr, userAgent):
        self.browser = browser
        if headlessStr.lower() == "true":
            self.headless = True
        else:
            self.headless = False
        self.userAgent = userAgent

        x = threading.Thread(
            target=self._downloadDriver
        )
        x.start()

    def _downloadDriver(self):
        """ Creates selenium driver for webscrapping automation
            Downloads it into driver folder if not installed
        """

        if not self.driverFolder.exists():
            os.mkdir("driver")

        msgTxt = "User agent: " + self.userAgent + "<br>"
        self.announcer.announce(self.announcer.format_sse(msgTxt))

        for browserVersion in self.userAgent.split(" "):
            if browserVersion.split("/")[0] == self.browser:
                version = browserVersion.split("/")[1]
        if len(version) == 0:
            # output += "Browser not found, options are -
            # Mozilla,
            # AppleWebKit,
            # Chrome,
            # Safari,
            # Edg
            msgTxt = "Error: Browser not found, options are - Chrome, Edg <br>"
            self.announcer.announce(self.announcer.format_sse(msgTxt))

        # get driver path
        self.driverInstalledBool, self.driverPath = self.getDriverPath(
            self.driverFolder,
            self.browser
        )

        # download driver
        if not self.driverInstalledBool:
            msgTxt = "Installing driver <br>"
            self.announcer.announce(self.announcer.format_sse(msgTxt))

            if self.browser == "Chrome":
                browserDriverDownloadPage, _, _ = download.getRequest(
                    "https://chromedriver.chromium.org/downloads"
                )
                pattern = r"ChromeDriver (" \
                    + version.split(".")[0] \
                    + r"\.\d*\.\d*\.\d*)"
                existingDriverVersion = re.findall(
                    pattern,
                    browserDriverDownloadPage.content.decode("utf-8")
                )[0]
                browserDriverDownloadUrl = \
                    "https://chromedriver.storage.googleapis.com/" \
                    + existingDriverVersion \
                    + "/chromedriver_win32.zip"
            elif self.browser == "Edg":
                browserDriverDownloadUrl = \
                    "https://msedgedriver.azureedge.net/" \
                    + version \
                    + "/edgedriver_win64.zip"
            else:
                print("Browser not supported yet")

            msgTxt = "Driver URL: " + browserDriverDownloadUrl + "<br>"
            self.announcer.announce(self.announcer.format_sse(msgTxt))

            driverRequest = download.getRequest(browserDriverDownloadUrl)[0]
            driverZip = zipfile.ZipFile(io.BytesIO(driverRequest.content))
            driverZip.extractall(self.driverFolder)

            msgTxt = "Downloaded and extracted driver <br>"
            self.announcer.announce(self.announcer.format_sse(msgTxt))

            # get driver path
            self.driverInstalledBool, self.driverPath = self.getDriverPath(
                self.driverFolder,
                self.browser
            )
        else:
            msgTxt = "Driver already satisfied <br>"
            self.announcer.announce(self.announcer.format_sse(msgTxt))

        # Create driver
        self.driver = self.createDriver(
            self.browser,
            self.driverPath,
            self.headless
        )

        msgTxt = "Started Driver <br>"
        self.announcer.announce(self.announcer.format_sse(msgTxt))

    def createDriver(self, browser, driverPath, headless=None):
        """ Start selenium web driver

        Args:
            browser (str): Browser type
            driverPath (Path): Path to driver
            headless (bool): Headless bool

        Returns:
            driver: selenium driver
        """

        self.headless = headless

        if browser == "Edg":
            edge_options = EdgeOptions()
            if self.headless:
                # make Edge headless
                edge_options.use_chromium = True
                edge_options.add_argument("headless")
                edge_options.add_argument("disable-gpu")
                edge_options.add_argument("--log-level=3")
                edge_options.add_experimental_option(
                    'excludeSwitches',
                    ['enable-logging']
                )
                # edge_options.page_load_strategy("eager")
            self.driver = Edge(
                executable_path=str(driverPath),
                options=edge_options
            )
        elif browser == "Chrome":
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--log-level=3")
                chrome_options.add_experimental_option(
                    'excludeSwitches',
                    ['enable-logging']
                )
                # chrome_options.page_load_strategy("eager")
                # don't know the chrome command
            self.driver = webdriver.Chrome(
                executable_path=str(driverPath),
                options=chrome_options
            )
        else:
            print("Browser not supported yet")

        self.driver.set_window_size(1800, 1080)
        self.driver.set_page_load_timeout(100000)

        return self.driver
