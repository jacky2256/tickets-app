import csv
import os
import logging
import random
from typing import Optional, Collection

from app.schemas import EntryKeywords, EntryKeyword, OutputKeywords
from app.settings import OUT_DIR, IN_DIR, PROXIES_FILE_PATH


def read_lines(fn: str) -> Collection[str]:
    """
    Read text file.
    :param fn: File path
    :return:  An iterator
    """
    result = []
    try:
        with open(fn, mode="rt", encoding='utf8', errors='replace') as infile:
            for line in infile:
                result.append(line.rstrip('\n'))
    except IOError as e:
        logging.error(e)
    return result

def save_content_in_file(content: str, directory='output_content',
                         filename='output_linkedin', extension='html'):
    try:
        path_dir = os.path.join(str(OUT_DIR.absolute()), directory)
        if not os.path.exists(path_dir):
            os.makedirs(path_dir)
        path = f"{path_dir}/{filename}.{extension}"
        with open(path, 'w', encoding='utf-8') as file:
            file.write(content)
    except OSError as err:
        logging.error(f"OS error occured: {err}")
    except Exception as err:
        logging.error(f"Unexpected error occurred: {err}")


def read_csv_to_entry_keywords(file_path: str) -> Optional[EntryKeywords]:
    try:
        keywords = []
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = list(csv.DictReader(csvfile))
            if not reader:
                return EntryKeywords(keywords=keywords)

            default_artist = reader[0]['artist'].strip()

            for index, row in enumerate(reader):
                city = row['Keyword'].strip()
                keyword_name = f"{city} {default_artist}".strip()
                keywords.append(EntryKeyword(id=index + 1, name=keyword_name))

        return EntryKeywords(keywords=keywords)
    except Exception as err:
        logging.error(f"Unexpected error occurred: {err}")
        return None

def save_output_keywords_to_csv(output_keywords: OutputKeywords, file_path: str) -> bool:
    try:
        with open(file_path, mode="w", newline='', encoding="utf-8") as csvfile:
            fieldnames = ["id", "name", "min_price_vivid", "min_price_ticket"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for keyword in output_keywords.keywords:
                writer.writerow({
                    "id": keyword.id,
                    "name": keyword.name,
                    "min_price_vivid": keyword.min_price_vivid,
                    "min_price_ticket": keyword.min_price_ticket
                })
        return True
    except Exception as err:
        logging.error(f"Error writing CSV file: {err}")
        return False

def import_proxies():
    try:
        file_path = str(PROXIES_FILE_PATH.absolute())
        lines = read_lines(str(file_path))
        lines = list(lines)
        if lines:
            logging.info(f"Proxies imported: {len(lines)}")
            random.shuffle(lines)
            return lines
        else:
            raise IOError("Empty proxies. Exit")
    except Exception as err:
        raise SystemExit(f"Error with import proxies {err}")