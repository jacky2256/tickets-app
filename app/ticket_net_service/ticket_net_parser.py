import json
import re
import logging
import urllib.parse
from typing import List, Any

from parsel import Selector
from concurrent.futures import ThreadPoolExecutor

from app.settings import VIVID_THREADS
from app.wdm import SBDriver
from app.utils import save_content_in_file
from app.schemas import OutputKeyword, OutputKeywords


class TickNetSearchPage:
    BASE_URL = "https://www.ticketnetwork.com"

    def generate_search_url(self, query: str) -> str:
        try:
            encoded_query = urllib.parse.quote(query)
            return f"{self.BASE_URL}/search?q={encoded_query}"
        except Exception as err:
            logging.error(f"Error generating search URL: {err}")
            return ""

    @staticmethod
    def extract_ticket_link(selector: Selector) -> str:
        result_link = ''
        try:
            text = selector.xpath(
                "//div[contains(@class, 'event-list-items')]/script/text()"
            ).get(default="")
            if text.strip():
                result_link = text.strip()
        except Exception as err:
            logging.error(f"Error extracting ticker link: {err}")
        return result_link


class TickNetTicketsPage:
    @staticmethod
    def extract_low_price(selector: Selector) -> str:
        result_price = ''
        try:
            text = selector.xpath(
                "(//table[contains(@class, 'venue-ticket-list-tbl')][1]//table)[1]"
                "//span[contains(@class, 'sea-ticket-list-price-col-price')]/span[1]/text()"
            ).get(default="")
            if text.strip():
                result_price = text.strip()
        except Exception as err:
            logging.error(f"Error extracting low price: {err}")
        return result_price


class TickNetService(TickNetSearchPage, TickNetTicketsPage):
    def __init__(self):
        super().__init__()

    def process(self, entries: OutputKeywords) -> OutputKeywords:
        results = OutputKeywords(keywords=[])

        try:
            keywords = entries.keywords
            with ThreadPoolExecutor(max_workers=VIVID_THREADS) as executor:
                processed_keywords = executor.map(lambda keyword: OutputKeyword(
                    id=keyword.id,
                    name=keyword.name,
                    min_price_vivid=keyword.min_price_vivid,
                    min_price_ticket=self.worker(keyword.name,),
                ), keywords)

            results.keywords.extend(processed_keywords)

        except Exception as err:
            logging.error(f"Error in process method: {err}")

        return results

    def worker(self, query: str) -> int:
        min_price = 0
        try:
            url = self.generate_search_url(query)
            logging.info(f"Ticket Net search url: {url}")
            content_search_url = self.fetch_content(url)
            save_content_in_file(content_search_url, filename=f"{query}_search.html")

            if content_search_url:
                selector = Selector(content_search_url)
                ticket_list_string = self.extract_ticket_link(selector)
                ticket_list = self.parse_json_string_to_list(ticket_list_string)
                ticket_link = self.extract_first_url(ticket_list)
                logging.info(f"Ticket Net ticket link: {ticket_link}")
                if ticket_link:
                    content_ticket_url = self.fetch_content(ticket_link)
                    save_content_in_file(content_ticket_url, filename=f"{query}_ticket.html")
                    selector = Selector(content_ticket_url)
                    min_price_text = self.extract_low_price(selector)
                    logging.info(f"Ticket Net ticket text price: {min_price_text}")
                    if min_price_text:
                        min_price = self.extr_price_from_str(min_price_text)
                        logging.info(f"Ticket Net ticket price: {min_price}")

        except Exception as err:
            logging.error(err)
        return min_price

    @staticmethod
    def fetch_content(url: str) -> str:
        result_content = ''
        try:
            proxy = "socks5://156.239.60.140:1080"
            result_content = SBDriver().fetch_content(url, proxy=proxy)
        except Exception as err:
            logging.error(err)
        return result_content

    @staticmethod
    def extr_price_from_str(price_str: str) -> int:
        result_price = 0
        try:
            match = re.search(r"\$(\d+)", price_str)
            if match:
                result_price = int(match.group(1))
        except Exception as err:
            logging.error(f"Error parsing price: {err}")
        return result_price

    @staticmethod
    def parse_json_string_to_list(json_string: str) -> List[Any]:
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as err:
            logging.error(f"Error parsing JSON string: {err}")
            return []

    @staticmethod
    def extract_first_url(json_list: List[Any]) -> str:
        result_url = ''
        try:
            if json_list and isinstance(json_list[0], dict) and "url" in json_list[0]:
                result_url = json_list[0]["url"]
        except Exception as err:
            logging.error(f"Error extracting URL: {err}")
        return result_url

if __name__ == "__main__":
    query_1 = "Chicago bibi"
    query_2 = "Boston bibi"

    keyword_1 = OutputKeyword(id=0, name=query_1, min_price_vivid=120, min_price_ticket=0)
    keyword_2 = OutputKeyword(id=1, name=query_2, min_price_vivid=95, min_price_ticket=0)
    entries_ = OutputKeywords(keywords=[keyword_1, keyword_2])

    vivid_service = TickNetService()
    results = vivid_service.process(entries_)
    print(results)
