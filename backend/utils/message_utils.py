from typing import Dict


def format_message(sender: str, content: str) -> Dict[str, str]:
    return {"sender": sender, "content": content.strip()}


