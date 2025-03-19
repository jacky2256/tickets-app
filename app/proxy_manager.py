import logging
import threading, math
from queue import Queue
from typing import Optional
from app.settings import MAX_FAILURES_PER_ONE_PROXY


class ProxyManager:
    def __init__(self, proxies: list):
        self.good_proxies = Queue()
        self.failed_proxies = {}
        self.banned_proxies = set()
        self.max_failures = MAX_FAILURES_PER_ONE_PROXY
        self.total_proxies = len(proxies)
        self.lock = threading.Lock()
        self.__import_proxies__(proxies)

    def __import_proxies__(self, proxies):
        try:
                for proxy in proxies:
                    self.good_proxies.put(proxy)
        except Exception as err:
            raise SystemExit(f"Error with import proxies {err}")

    def get_proxy(self) -> Optional[str]:
        try:
            with self.lock:
                if not self.good_proxies.empty():
                    proxy = self.good_proxies.get()
                    if proxy not in self.banned_proxies:
                        self.good_proxies.put(proxy)
                        return proxy
        except Exception as err:
            logging.error(err)
        return

    def put_proxy(self, proxy, is_bad: bool = False):
        try:
            if is_bad:
                self.report_failure(proxy)
            else:
                self.report_success(proxy)
        except Exception as err:
            logging.error(err)

    def report_failure(self, proxy: str):
        try:
            with self.lock:
                if proxy in self.banned_proxies:
                    return

                if proxy in self.failed_proxies:
                    self.failed_proxies[proxy] += 1
                else:
                    self.failed_proxies[proxy] = 1

                num_failures = self.failed_proxies[proxy]
                if num_failures >= self.max_failures:
                    self.banned_proxies.add(proxy)
                    self.failed_proxies.pop(proxy)
                else:
                    self.good_proxies.put(proxy)
        except Exception as err:
            logging.error(err)

    def report_success(self, proxy: str):
        try:
            with self.lock:
                if proxy in self.failed_proxies:
                    self.failed_proxies.pop(proxy)
                self.good_proxies.put(proxy)
        except Exception as err:
            logging.error(err)
        return

    def check_banned_proxies(self):
        try:
            num_banned_proxies = len(self.banned_proxies)
            max_durable_proxies = math.ceil((self.total_proxies * 85) / 100)
            if num_banned_proxies >= max_durable_proxies:
                return True
        except Exception as err:
            logging.error(err)
        return False

def my_func():
    return

if __name__ == '__main__':
    print(my_func())