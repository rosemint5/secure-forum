import re

def sanitize_for_log(value, max_len=128):
    if not value:
        return "-"
    value = str(value)

    # neutralize log-breaking characters
    value = value.replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")

    # allow only printable ASCII
    value = re.sub(r"[^\x20-\x7E]", "?", value)

    return value[:max_len]

def get_client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if xff:
        return sanitize_for_log(xff.split(",")[0].strip(), max_len=45)
    return sanitize_for_log(request.META.get("REMOTE_ADDR"), max_len=45)
