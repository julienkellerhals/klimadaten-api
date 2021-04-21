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
        return render_template(
            "stream.html",
            streamUrl="/admin/stream/idaweb"
        )

    return scrapeApi
