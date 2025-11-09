import pytest
from src.scraper.image_handler import NPCImageExtractor


@pytest.fixture
def html_content() -> str:
    fixture_path = "tests/fixtures/Abyssal_guardian_(Guardians_of_the_Rift).html"

    with open(fixture_path, "r", encoding="utf-8") as f:
        return f.read()


def test_extract_image_url(html_content: str):
    extractor = NPCImageExtractor()
    image_url = extractor.extract_image_url(html_content)

    expected_url = "https://oldschool.runescape.wiki/images/Abyssal_guardian_(Guardians_of_the_Rift).png"
    print(f"Extracted image URL: {image_url}")
    assert image_url.image_url == expected_url


# def test_download_npc_image(html_content: str):
#     import asyncio

#     extractor = NPCImageExtractor()
#     image_url_result = extractor.extract_image_url(html_content)
#     image_url = image_url_result.image_url

#     assert image_url is not None, "Image URL should not be None"

#     result = asyncio.run(extractor.download_npc_image(image_url))
#     assert result.success is True
