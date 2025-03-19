import redis
from app.schemas import OutputKeywords, EntryKeywords, OutputKeyword

redis_client = redis.Redis(host="redis", port=6379, db=0, decode_responses=True, username='default', password='guest')

def save_keywords_to_redis(entry_keywords: EntryKeywords):
    output_keywords = OutputKeywords(
        keywords=[
            OutputKeyword(id=kw.id, name=kw.name, min_price_vivid=0, min_price_ticket=0)
            for kw in entry_keywords.keywords
        ]
    )

    redis_client.set("output_keywords", output_keywords.model_dump_json())

def get_keywords_from_redis() -> OutputKeywords:
    data = redis_client.get("output_keywords")
    if data:
        return OutputKeywords.model_validate_json(data)
    return OutputKeywords(keywords=[])

def update_keywords_in_redis(updated_keywords: OutputKeywords):
    redis_client.set("output_keywords", updated_keywords.model_dump_json())

def delete_all_keywords_from_redis():
    redis_client.delete("output_keywords")

def get_status_keywords() -> bool:
    """Retrieve status and convert it back to a boolean"""
    status = redis_client.get("status")
    return status == "true"
def set_status_keywords(status: bool = False):
    """Process is running when status is True"""
    redis_client.set("status", str(status).lower())
