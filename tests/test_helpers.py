from pathlib import Path
import pytest

from src.utils.helpers import url_to_filename, extract_npc_name_from_url


def test_url_to_filename():
    url_1 = "https://oldschool.runescape.wiki/w/Barman_(King%27s_Axe_Inn)"
    expected_filename_1 = "Barman_(King%27s_Axe_Inn).html"
    assert url_to_filename(url_1) == expected_filename_1

    # potential edge cases
    url_2 = "https://oldschool.runescape.wiki/w/%3F_%3F_%3F_%3F"
    expected_filename_2 = "%3F_%3F_%3F_%3F.html"
    assert url_to_filename(url_2) == expected_filename_2

    url_3 = "https://oldschool.runescape.wiki/w/50%25_Luke"
    expected_filename_3 = "50%25_Luke.html"
    assert url_to_filename(url_3) == expected_filename_3

    # images
    url_4 = "https://oldschool.runescape.wiki/images/50%25_Luke.png"
    expected_filename_4 = "50%25_Luke.png"
    assert url_to_filename(url_4, extension=None) == expected_filename_4


def test_extract_npc_name_from_url():
    url = "https://oldschool.runescape.wiki/w/Barman_(King%27s_Axe_Inn)"
    expected_name = "Barman (King's Axe Inn)"
    assert extract_npc_name_from_url(url) == expected_name

    # potential edge cases
    url_2 = "https://oldschool.runescape.wiki/w/%3F_%3F_%3F_%3F"
    expected_name = "? ? ? ?"
    assert extract_npc_name_from_url(url_2) == expected_name

    url_3 = "https://oldschool.runescape.wiki/w/50%25_Luke"
    expected_name = "50% Luke"
    assert extract_npc_name_from_url(url_3) == expected_name
