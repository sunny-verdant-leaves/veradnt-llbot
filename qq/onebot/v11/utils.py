"""OneBot v11 辅助函数。"""


def escape(s: str, *, escape_comma: bool = True) -> str:
    """对字符串进行 CQ 码转义

    Args:
        s: 需要转义的字符串
        escape_comma: 是否转义逗号`,`
    """
    s = s.replace("&", "&amp;").replace("[", "&#91;").replace("]", "&#93;")
    if escape_comma:
        s = s.replace(",", "&#44;")
    return s


def unescape(s: str) -> str:
    """对字符串进行 CQ 码去转义

    Args:
        s: 需要转义的字符串
    """
    return (
        s.replace("&#44;", ",")
        .replace("&#91;", "[")
        .replace("&#93;", "]")
        .replace("&amp;", "&")
    )