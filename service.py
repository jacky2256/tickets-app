# import os
# import openpyxl
# from typing import List, Dict
import logging
from schemas import EntryKeywords
from cache import update_keywords_in_redis, save_keywords_to_redis, delete_all_keywords_from_redis, set_status_keywords
# from settings import XLSX_FILE_PATH
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
        except Exception as err:
            logging.error(err)
        finally:
            set_status_keywords(False)
            logging.info("END PROCESSING!")

# class FileReaderService:
#
#     def process_ser(self):
#         try:
#             file_path = str(XLSX_FILE_PATH.absolute())
#             self.read_event_data_from_xlsx(file_path)
#         except Exception as err:
#             logging.error(err)
#
#     @staticmethod
#     def read_event_data_from_xlsx(file_path: str) -> List[Dict[str, str]]:
#         """
#         Считывает данные из XLSX-файла, начиная с 5-й строки, и возвращает список словарей.
#         """
#         START_NUM_CELL = 5
#         HEADERS = [
#             "Event Date", "Presale Date", "Presale Time (EST)", "Presale Type", "City", "State", "Venue",
#             "Capacity", "Min Price (Vivid)", "Min Price (Ticket Network)", "Min Cost", "Max Cost"
#         ]
#
#         workbook = openpyxl.load_workbook(file_path, data_only=True)
#         sheet = workbook.active
#         event_data = []
#
#         for row in sheet.iter_rows(min_row=START_NUM_CELL, max_row=sheet.max_row, values_only=True):
#             if all(cell is None for cell in row):
#                 continue
#             row_data = {header: (str(value) if value is not None else "N/A") for header, value in zip(HEADERS, row)}
#             event_data.append(row_data)
#
#         workbook.close()
#         return event_data


# if __name__ == '__main__':
#     file_path = str(XLSX_FILE_PATH.absolute())
#     print(file_path)
#     service = FileReaderService()
#     results = service.read_event_data_from_xlsx(file_path)
#     for i in results:
#         print(i)
