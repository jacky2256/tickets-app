import logging
from schemas import EntryKeywords
from cache import update_keywords_in_redis, save_keywords_to_redis, delete_all_keywords_from_redis, set_status_keywords
from vivid_service.vivid_parser import VividService
from ticket_net_service.ticket_net_parser import TickNetService

class MainProcess:
    @staticmethod
    def process_ser(entries: EntryKeywords):
        try:
            delete_all_keywords_from_redis()
            save_keywords_to_redis(entries)
            vivid_service = VividService()
            results_vivid = vivid_service.process(entries)
            update_keywords_in_redis(results_vivid)

            ticket_net_service = TickNetService()
            results_ticket_net = ticket_net_service.process(results_vivid)
            update_keywords_in_redis(results_ticket_net)
            set_status_keywords(False)
        except Exception as err:
            logging.error(err)
