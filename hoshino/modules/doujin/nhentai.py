from collections import namedtuple
from enum import Enum, unique
from typing import List
from urllib.parse import urljoin

import requests


@unique
class Extension(Enum):
    JPG = 'j'
    PNG = 'p'
    GIF = 'g'


class Doujin():
    """
	Class representing a doujin.

	:ivar int id:			Doujin id.
	:ivar dict titles:		Doujin titles (language:title).
	:ivar Doujin.Tag tags:	Doujin tag list.
	:ivar str cover:		Doujin cover image url.
	:ivar str thumbnail:	Doujin thumbnail image url.
	"""
    Tag = namedtuple("Tag", ["id", "type", "name", "url", "count"])
    Pages = namedtuple("Page", ["url", "width", "height"])

    def __init__(self, data):
        self.id = data["id"]
        self.media_id = data["media_id"]
        self.titles = data["title"]
        self.favorites = data["num_favorites"]
        self.url = f"https://nhentai.net/g/{self.id}"
        images = data["images"]

        self.pages = [Doujin.__makepage__(self.media_id, num, **_) for num, _ in enumerate(images["pages"], start=1)]
        self.tags = [Doujin.Tag(**_) for _ in data["tags"]]

        thumb_ext = Extension(images["thumbnail"]["t"]).name.lower()
        self.thumbnail = f"https://t.nhentai.net/galleries/{self.media_id}/thumb.{thumb_ext}"

        cover_ext = Extension(images["cover"]["t"]).name.lower()
        self.cover = f"https://t.nhentai.net/galleries/{self.media_id}/cover.{cover_ext}"

    def __getitem__(self, key: int):
        """
		Returns a page by index.

		:rtype: Doujin.Page 
		"""
        return self.pages[key]

    def __makepage__(media_id: int, num: int, t: str, w: int, h: int):
        return Doujin.Pages(f"https://i.nhentai.net/galleries/{media_id}/{num}.{Extension(t).name.lower()}",
                            w, h)


_SESSION = requests.Session()


def _get(endpoint, params={}) -> dict:
    return _SESSION.get(urljoin("https://nhentai.net/api/", endpoint), params=params).json()


def search(query: str, page: int = 1, sort_by: str = "date") -> List[Doujin]:
    """
	sSearch doujins by keyword.

	:param str query: Search term. (https://nhentai.net/info/)
	:param int page: Page number. Defaults to 1.
	:param str sort_by: Method to sort search results by (popular/date). Defaults to date.

	:returns list[Doujin]: Search results parsed into a list of nHentaiDoujin objects
	"""
    galleries = _get('galleries/search', {"query": query, "page": page, "sort": sort_by})["result"]
    return [Doujin(search_result) for search_result in galleries]


def search_tagged(tag_id: int, page: int = 1, sort_by: str = "date") -> List[Doujin]:
    """
	Search doujins by tag id.

	:param int tag_id: Tag id to use.
	:param int page: Page number. Defaults to 1.
	:param str sort_by: Method to sort search results by (popular/date). Defaults to date.

	:returns list[Doujin]: Search results parsed into a list of nHentaiDoujin objects
	"""
    try:
        galleries = _get('galleries/tagged', {"tag_id": tag_id, "page": page, "sort": sort_by})["result"]
    except KeyError:
        raise ValueError("There's no tag with the given tag_id.")

    return [Doujin(search_result) for search_result in galleries]


def get_homepage(page: int = 1) -> List[Doujin]:
    """
	Get recently uploaded doujins from the homepage.

	:param int page: Page number. Defaults to 1.

	:returns list[Doujin]: Search results parsed into a list of nHentaiDoujin objects
	"""
    return [Doujin(recent) for recent in _get('galleries/all', {"page": page})["result"]]


def get_doujin(id: int) -> Doujin:
    """
	Get a doujin by its id.

	:param int id: A doujin's id.

	:rtype: Doujin
	"""
    try:
        return Doujin(_get(f"gallery/{id}"))
    except KeyError:
        raise ValueError("A doujin with the given id wasn't found")


def get_random_id() -> int:
    """
	Get an id of a random doujin.

	:returns int: A random existing doujin id.
	"""
    redirect = _SESSION.head("https://nhentai.net/random/").headers["Location"]
    return int(redirect[3:-1])
