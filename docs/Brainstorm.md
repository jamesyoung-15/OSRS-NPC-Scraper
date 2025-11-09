# OSRS Wiki NPC Scraping Project Brainstorm

Brainstorm stuff.

## Project Description

This repo should crawl the OSRS NPC wiki to at the bare minimum go through the NPC character list page, grab all NPC names and links to their respective individual wiki page, then crawl and scrape the HTML content and save them (alongside thumbnail images). The saved HTML pages can be used for further downstream processing.

For downstream processing, I am thinking of filtering out non-NPC characters (eg. fishes, birds), NPC characters without locations, and perhaps NPCs without names (Factory Manager, Farmer, etc.).

Then, I can grab wiki description and summary of the NPC, geolocation, etc. for different applications like building a Geoguessr game, text analysis of wiki pages, etc.

## Tech Stack

- Scraping
  - httpx (make async http requests)
  - BeautifulSoup4 (parse HTML and extract data)

- Data Storage
  - SQLite + SQLAlchemy (lightweight to store NPC data or other data needed later)
  - Redis (tracking visited URLs, manage crawl queue, etc.)

## Components

### 1. Wiki Scraping

This is pretty straightforward process, just need to make sure to rate limit to avoid ban. The HTML files and images are not large so even with 4315 NPCs, space and downloading content won't be an issue.

#### Pipeline

1. Crawl and Queue individual NPC Wiki Links

- Start from [NPC category page](https://oldschool.runescape.wiki/w/Category:Non-player_characters)
- Grab each character link, queue them up
- Go to next page link until we reach the end

2. Extract individual NPC Wiki Pages

- Vist each NPC link in queue
- Download HTML page
- Download image thumbnail of NPC if it exists
- Add basic info (NPC name, HTML path, URL paths) to DB

### 2. Geolocation Extraction and Filtering NPCs

We can filter out most non-character NPCs pretty easily since most character NPCs have some geolocation data and other info (eg. race).

Filtering out NPCs with non-generic names may be a bit harder, we can use NER (Named Entity Recognition) but there are some notable NPCs (eg. Wise Old man) that may need special exception.

I also want the geolocation data (longitude and latitude) since I want to build a NPC Geoguessr game.

Currently implementing and ongoing