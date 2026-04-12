import tiktoken
import traceback
from modules.helpers.logging_helper import logger


def get_num_tokens_from_string(string: str, encoding_name: str) -> int:
    try:
        encoding = tiktoken.encoding_for_model(encoding_name)
        return len(encoding.encode(string))
    except Exception:
        logger.warning(f"Failed to get encoding for model {encoding_name} due to {traceback.format_exc()}. Falling back to word count for token estimation.")
        # Fallback: approximate by word count
        return len(string.split())