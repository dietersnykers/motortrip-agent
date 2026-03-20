import re


def extract_day_reference(user_input: str, current_day: int) -> int | None:
    text = user_input.lower()

    if "vandaag" in text:
        return current_day

    if "morgen" in text:
        return current_day + 1

    match = re.search(r"dag\s+(\d+)", text)
    if match:
        return int(match.group(1))

    if text.strip().isdigit():
        return int(text.strip())

    standalone_number = re.search(r"\b(\d+)\b", text)
    if standalone_number:
        return int(standalone_number.group(1))

    return None


def detect_intent(user_input: str) -> str | None:
    text = user_input.lower().strip()

    if text in ["stop", "quit", "exit"]:
        return "stop"

    if text in ["help", "hulp", "wat kan je", "wat kun je", "help me"]:
        return "help"

    if text == "dag":
        return "show_day"

    if text.startswith("zet dag"):
        return "set_day"

    if any(word in text for word in ["hotel", "slapen", "overnachten"]):
        return "hotel"

    if any(word in text for word in ["highlight", "highlights", "fotoplek", "foto", "beziens", "mooi onderweg"]):
        return "highlights"

    if any(word in text for word in ["route", "afstand", "rijden", "traject"]):
        return "route"

    if any(word in text for word in ["briefing", "samenvatting", "vertel over", "wat mogen we verwachten"]):
        return "briefing"

    return None


def extract_set_day_value(user_input: str) -> int | None:
    match = re.search(r"zet\s+dag\s+(\d+)", user_input.lower())
    if match:
        return int(match.group(1))
    return None