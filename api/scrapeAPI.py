from flask import Blueprint
from flask import render_template
import webscraping


def constructBlueprint(announcer, instance, abstractDriver):
    scrapeApi = Blueprint("scrapeApi", __name__)

    @scrapeApi.route("/", methods=["GET", "POST"])
    def scrape():
        webscraping.scrape_meteoschweiz(
            abstractDriver,
            instance,
            announcer
        )
        webscraping.scrape_idaweb(
            abstractDriver,
            instance,
            announcer
        )

        return "Finished scrapping"

    @scrapeApi.route("/meteoschweiz", methods=["GET"])
    def scrapeMeteoschweizGet():
        """ Return meteosuisse page

        Returns:
            html: Renders html template
        """

        return render_template(
            "stream.html",
            streamUrl="/admin/stream/meteoschweiz"
        )

    @scrapeApi.route("/meteoschweiz", methods=["POST"])
    def scrapeMeteoschweizPost():
        _ = webscraping.scrape_meteoschweiz(
            abstractDriver,
            instance,
            announcer
        )

        return "Finished scrapping meteoschweiz"

    @scrapeApi.route("/idaweb", methods=["GET"])
    def scrapeIdawebGet():
        """ Return idaweb page

        Returns:
            html: Renders html template
        """

        return render_template(
            "stream.html",
            streamUrl="/admin/stream/idaweb"
        )

    @scrapeApi.route("/idaweb", methods=["POST"])
    def scrapeIdawebPost():
        _ = webscraping.scrape_idaweb(
            abstractDriver,
            instance,
            announcer
        )

        return "Finished scrapping idaweb"

    return scrapeApi
