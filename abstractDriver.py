import os
import io
import zipfile
import threading
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from msedge.selenium_tools import EdgeOptions
from msedge.selenium_tools import Edge
import download
import messageAnnouncer


class AbstractDriver():
    driver = None
    browser = None
    driverPath = None
    driverInstalledBool = False
    headless = False
    announcer = None
    statusStream = None

    def __init__(self):
        self.statusStream = messageAnnouncer.MessageAnnouncer()

    def runThreaded(
            self,
            announcer,
            browser,
            headlessStr,
            userAgent):
        self.announcer = announcer
        x = threading.Thread(
            target=self.downloadDriver,
            args=(browser, headlessStr, userAgent)
        )
        x.start()

    def getDriverStatus(self):
        x = threading.Thread(
            target=self._getDriverStatus
        )
        x.start()

    def _getDriverStatus(self):
        try:
            self.driver.window_handles
        except WebDriverException as e:
            msgTxt = "Status: 1; Error: " + str(e)
            self.statusStream.announce(self.statusStream.format_sse(msgTxt))
        except AttributeError as e:
            msgTxt = "Status: 1; Error: " + str(e)
            self.statusStream.announce(self.statusStream.format_sse(msgTxt))
        else:
            msgTxt = "Status: 0; Instance: " \
                + str(self.driver.window_handles[0])
            self.statusStream.announce(self.statusStream.format_sse(msgTxt))

    def checkDriver(self):
        if self.driver is None:
            print("Driver not started")
            print("Starting programatically")
            print("Assuming you installed only required drivers")
            cwd = Path.cwd()
            driverFolder = cwd / "driver"
            _, self.driverPath = self.getDriverPath(driverFolder, None)
            if self.driverPath.name == "msedgedriver.exe":
                self.browser = "Edg"
            elif driverPath.name == "chromedriver.exe":
                self.browser = "Chrome"
            else:
                print("Browser not supported yet")
            # make browser headless or not
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
                self.driverPath = driverPath
        return self.driverInstalledBool, self.driverPath

    def downloadDriver(self, browser, headlessStr, userAgent):
        """ Creates selenium driver for webscrapping automation
            Downloads it into driver folder if not installed

        Args:
            browser (string): Browser type (Edge, Chrome, etc.)
            headlessStr (string): Start in headless bool
            userAgent (string): Browser user agent from header
        """

        cwd = Path.cwd()
        driverFolder = cwd / "driver"
        if not driverFolder.exists():
            os.mkdir("driver")

        msgTxt = "User agent: " + userAgent + "<br>"
        self.announcer.announce(self.announcer.format_sse(msgTxt))

        for browserVersion in userAgent.split(" "):
            if browserVersion.split("/")[0] == browser:
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
            driverFolder,
            browser
        )

        # download driver
        if not self.driverInstalledBool:
            msgTxt = "Installing driver <br>"
            self.announcer.announce(self.announcer.format_sse(msgTxt))

            if browser == "Chrome":
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
            elif browser == "Edg":
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
            driverZip.extractall(driverFolder)

            msgTxt = "Downloaded and extracted driver <br>"
            self.announcer.announce(self.announcer.format_sse(msgTxt))

            # get driver path
            self.driverInstalledBool, self.driverPath = self.getDriverPath(
                driverFolder,
                browser
            )
        else:
            msgTxt = "Driver already satisfied <br>"
            self.announcer.announce(self.announcer.format_sse(msgTxt))

        # Convert to string
        if headlessStr.lower() == "true":
            headlessBool = True
        else:
            headlessBool = False

        # Create driver
        self.driver = self.createDriver(browser, self.driverPath, headlessBool)

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
