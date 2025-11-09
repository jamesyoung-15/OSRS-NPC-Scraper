from typing import Optional

from urllib.parse import urlparse, unquote


def url_to_filename(url: str, extension: Optional[str] = "html") -> str:
    """
    Convert a URL to a filename, keeps encoding for special characters.

    Args:
        url: The URL to convert
        extension: Whether to append an extension (default: 'html'), for downloading images, set to None

    Returns:
        Safe filename string

    Examples:
        >>> url_to_filename('https://oldschool.runescape.wiki/w/50%25_Luke')
        '50%25_Luke.html'
    """
    # extract path and filename, remove query and fragment
    path = urlparse(url).path
    filename = path.split("/")[-1]
    # filename = unquote(filename)
    filename = filename.split("#")[0]

    if not filename:
        filename = "unnamed"

    if extension is None:
        return filename
    return f"{filename}.{extension}"


def extract_npc_name_from_url(url: str) -> str:
    """
    Extract NPC name from wiki URL, converting underscores to spaces and decoding percent-encoded characters.

    Args:
        url: Wiki URL

    Returns:
        NPC name with underscores replaced by spaces

    Examples:
        >>> extract_npc_name_from_url('https://oldschool.runescape.wiki/w/50%25_Luke')
        '50% Luke'
    """
    path = urlparse(url).path
    name = path.split("/")[-1].split("#")[0]
    name = unquote(name)
    return name.replace("_", " ")
