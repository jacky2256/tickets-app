import re
import logging
import urllib.parse
from parsel import Selector
from concurrent.futures import ThreadPoolExecutor

from settings import VIVID_THREADS
from wdm import SBDriver
from utils import save_content_in_file
from schemas import EntryKeywords, OutputKeyword, OutputKeywords

class VividSearchPage:
    BASE_URL = "https://www.vividseats.com"

    def generate_search_url(self, query: str) -> str:
        try:
            encoded_query = urllib.parse.quote(query)
            return f"{self.BASE_URL}/search?searchTerm={encoded_query}"
        except Exception as err:
            logging.error(f"Error generating search URL: {err}")
            return ""

    def extract_ticket_link(self, selector: Selector) -> str:
        result_link = ''
        try:
            text = selector.xpath(
                "//div[@data-testid='productions-list']/div[1]/div[1]/a/@href"
            ).get(default="")
            if text.strip():
                result_link = f'{self.BASE_URL}{text}'
        except Exception as err:
            logging.error(f"Error extracting ticker link: {err}")
        return result_link


class VividTicketPage:
    @staticmethod
    def extract_low_price(selector: Selector) -> str:
        result_price = ''
        try:
            text = selector.xpath(
                "//button[contains(@data-testid, 'show-price-filter-button')]/span/text()"
            ).get(default="")
            if text.strip():
                result_price = text.strip()
        except Exception as err:
            logging.error(f"Error extracting low price: {err}")
        return result_price


class VividService(VividSearchPage, VividTicketPage):
    def __init__(self):
        super().__init__()

    def process(self, entries: EntryKeywords) -> OutputKeywords:
        results = OutputKeywords(keywords=[])

        try:
            keywords = entries.keywords
            with ThreadPoolExecutor(max_workers=VIVID_THREADS) as executor:
                processed_keywords = executor.map(lambda keyword: OutputKeyword(
                    id=keyword.id,
                    name=keyword.name,
                    min_price_vivid=self.worker(keyword.name,)
                ), keywords)

            results.keywords.extend(processed_keywords)
        except Exception as err:
            logging.error(f"Error in process method: {err}")

        return results

    def worker(self, query: str) -> int:
        min_price = 0
        try:
            url = self.generate_search_url(query)
            logging.info(f"Vivid search url: {url}")
            content_search_url = self.fetch_content(url)
            save_content_in_file(content_search_url, filename=f"{query}_search.html")

            if content_search_url:
                selector = Selector(content_search_url)
                ticket_link = self.extract_ticket_link(selector)
                logging.info(f"Vivid ticket link: {ticket_link}")
                if ticket_link:
                    content_ticket_url = self.fetch_content(ticket_link)
                    save_content_in_file(content_ticket_url, filename=f"{query}_ticket.html")
                    selector = Selector(content_ticket_url)
                    min_max_price_text = self.extract_low_price(selector)
                    logging.info(f"Vivid ticket text price: {min_max_price_text}")
                    if min_max_price_text:
                        min_price, max_price = self.extr_prices_from_str(min_max_price_text)
                        logging.info(f"Vivid ticket price: {min_price} - {max_price}")

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
    def extr_prices_from_str(price_str: str) -> tuple[int, int | None]:
        try:
            prices = list(map(int, re.findall(r'\d+', price_str.replace(',', ''))))

            if len(prices) == 2:
                return prices[0], prices[1]
            elif len(prices) == 1:
                return prices[0], None
            else:
                raise ValueError("Invalid price format")

        except Exception as err:
            logging.error(f"Error extracting prices: {err}")
            return 0, None


if __name__ == "__main__":
    from schemas import EntryKeyword

    query_1 = "Chicago bibi"
    query_2 = "Boston bibi"

    keyword_1 = EntryKeyword(id=0, name=query_1)
    keyword_2 = EntryKeyword(id=1, name=query_2)
    entries_ = EntryKeywords(keywords=[keyword_1, keyword_2])

    vivid_service = VividService()
    results = vivid_service.process(entries_)
    print(results)
