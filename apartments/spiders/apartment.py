import json

import scrapy
from scrapy.http import Response
from scrapy.http.response.html import HtmlResponse

MAX_APARTMENTS = 60
PAGE_STEP = 20


class ApartmentSpider(scrapy.Spider):
    name = "apartment"
    allowed_domains = ["realtylink.org"]
    api_url = "https://realtylink.org/Property/GetInscriptions"

    def start_requests(self):
        for start_pos in range(0, MAX_APARTMENTS, PAGE_STEP):
            request_body = {"startPosition": start_pos}
            yield scrapy.Request(
                url=self.api_url,
                method="POST",
                body=json.dumps(request_body),
                headers={"Content-Type": "application/json"},
                callback=self.parse,
            )

    def parse(self, response: Response, **kwargs) -> Response:
        data = json.loads(response.body)
        html_string = f"<html><body>{data['d']['Result']['html']}</body</html>"
        html_response = HtmlResponse(
            url="https://realtylink.org/en/properties~for-rent",
            body=html_string,
            encoding="utf-8",
        )
        apartments_link = html_response.css(
            "a.property-thumbnail-summary-link::attr(href)"
        ).getall()
        for apartment_link in apartments_link:
            yield html_response.follow(
                apartment_link,
                callback=self.parse_apartment,
                cb_kwargs={"apartment_link": apartment_link},
            )

    def parse_apartment(self, apartment: Response, apartment_link) -> dict:
        return {
            "link": apartment_link,
            "title": self._get_title(apartment),
            "address": self._get_address(apartment),
            "region": self._get_region(apartment),
            "description": self._get_description(apartment),
            "images": self._get_images(apartment),
            "price": self._get_price(apartment),
            "rooms": self._get_rooms(apartment),
            "area": self._get_area(apartment),
        }

    def _get_title(self, apartment: Response) -> str:
        return apartment.css("h1 > span::text").get(default="")

    def _get_address(self, apartment: Response) -> str:
        return apartment.css("div > div.d-flex.mt-1 > h2::text").get(default="").strip()

    def _get_region(self, apartment: Response) -> str:
        address = self._get_address(apartment)
        if "," in address:
            comma_index = address.index(",")
            return address[comma_index:].strip()
        return ""

    def _get_description(self, apartment: Response) -> str:
        return (
            apartment.css("div.row.description-row > div > div:nth-child(2)::text")
            .get(default="")
            .strip()
        )

    def _get_images(self, apartment: Response) -> list[str]:
        return apartment.css(
            "div.primary-photo-container > a > img::attr(src)"
        ).getall()

    def _get_price(self, apartment: Response) -> str:
        return apartment.css("div.price.text-right > span:nth-child(6)::text").get(
            default=""
        )

    def _get_rooms(self, apartment: Response) -> int:
        bedrooms_text = (
            apartment.css("div.col-lg-3.col-sm-6.cac::text")
            .get(default="")
            .strip()
            .split()
        )
        bedrooms = int(bedrooms_text[0]) if bedrooms_text else 0
        bathrooms_text = (
            apartment.css("div.col-lg-3.col-sm-6.sdb::text")
            .get(default="")
            .strip()
            .split()
        )
        bathrooms = int(bathrooms_text[0]) if bathrooms_text else 0
        return bedrooms + bathrooms

    def _get_area(self, apartment: Response) -> str:
        return (
            apartment.css("div:nth-child(1) > div.carac-value > span::text")
            .get(default="")
            .strip()
        )
