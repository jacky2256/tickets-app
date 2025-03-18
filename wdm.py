import logging
import time
from typing import Optional
from seleniumbase import SB
import sys
sys.argv.append("-n")


class SBDriver:
    @staticmethod
    def fetch_content(url: str, proxy: Optional[str] = None) -> str:
        content = ''
        try:
            with SB(
                    uc=True,
                    browser='chrome',
                    proxy=proxy,
            ) as sb:
                sb.time_limit = 20
                sb.get(url=url)
                content = sb.get_page_source()
                time.sleep(5)
        except Exception as err:
            logging.error(err)

        return content



