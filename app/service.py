import logging
from app.schemas import EntryKeywords
from app.cache import update_keywords_in_redis, save_keywords_to_redis, delete_all_keywords_from_redis, set_status_keywords
from app.utils import read_csv_to_entry_keywords, save_output_keywords_to_csv
from app.settings import INPUT_CSV_FILE_PATH, OUTPUT_CSV_FILE_PATH
from app.vivid_service.vivid_parser import VividService
from app.ticket_net_service.ticket_net_parser import TickNetService

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
        except Exception as err:
            logging.error(err)
        finally:
            set_status_keywords(False)
            logging.info("END PROCESSING!")

class FileReaderService:
    def __init__(self):
        logging.info("PROGRAM IS STARTING...")
        logging.info(f"Your results will save in {OUTPUT_CSV_FILE_PATH.absolute()}")

    def __del__(self):
        logging.info("PROGRAM FINISHED!")

    def process_ser(self):
        try:
            file_path = str(INPUT_CSV_FILE_PATH.absolute())
            output_file_path = str(OUTPUT_CSV_FILE_PATH.absolute())

            entries = read_csv_to_entry_keywords(file_path)
            if entries is None:
                logging.error("CSV FILE IS EMPTY!")
                return

            vivid_service = VividService()
            results_vivid = vivid_service.process(entries)

            ticket_net_service = TickNetService()
            results_ticket_net = ticket_net_service.process(results_vivid)
            is_saved_correct = save_output_keywords_to_csv(results_ticket_net, output_file_path)
            if is_saved_correct:
                logging.info(f"Data saved in {output_file_path}")
        except Exception as err:
            logging.error(err)



if __name__ == '__main__':
    servier = FileReaderService()
    servier.process_ser()
