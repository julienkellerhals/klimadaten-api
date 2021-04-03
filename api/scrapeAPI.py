from flask import Blueprint
from flask import render_template
import webscraping


def constructBlueprint(announcer, instance, abstractDriver):
    scrapeApi = Blueprint("scrapeApi", __name__)

    @scrapeApi.route("/meteoschweiz")
    def scrapeMeteoschweiz():
        """ Return meteosuisse page

        Returns:
            html: Renders html template
        """

        return render_template(
            "stream.html",
            streamUrl="/admin/stream/meteoschweiz"
        )

    @scrapeApi.route("/idaweb")
    def scrapeIdaweb():
        """ Runs idaweb scrapping

        Returns:
            str: temp
        """

        driver = abstractDriver.getDriver()
        engine = instance.getEngine()
        resp = webscraping.scrape_idaweb(driver, engine)
        return resp

    return scrapeApi
