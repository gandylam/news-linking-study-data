import datetime as dt
import re
from typing import List, Dict
import dateparser
import spacy
from bs4 import BeautifulSoup
from readability import Document

from analyzer.util import collections as collections
from analyzer.util.domains import get_canonical_mediacloud_domain

nlp = spacy.load('en_core_web_sm')


def extract_content(story_html: str) -> str:
    doc = Document(story_html)
    content = doc.summary()
    return content


# https://stackoverflow.com/questions/44078/strip-all-html-tags-except-links
TAGS_EXCEPT_LINKS_PATTERN = r"<(?!\/?a(?=>|\s.*>))\/?.*?>"


def remove_non_link_tags(story_content: str) -> str:
    return re.sub(TAGS_EXCEPT_LINKS_PATTERN, "", story_content)


def sentence_tokenization(story_content: str) -> List:
    doc = nlp(story_content)
    sentences = [str(s) for s in doc.sents]
    sentences = [s.strip() for s in sentences if len(s.strip()) > 0]
    return sentences


def country_alpha3(media_id: int) -> str:
    return collections.country_for_media(media_id)


def study_week_index(date_str: str) -> int:
    date = dateparser.parse(date_str).date()
    week_index = -1
    if (date >= dt.date(2020, 2, 2)) and (date <= dt.date(2020, 2, 8)):
        week_index = 1
    elif (date >= dt.date(2020, 5, 10)) and (date <= dt.date(2020, 5, 16)):
        week_index = 2
    elif (date >= dt.date(2020, 8, 16)) and (date <= dt.date(2020, 8, 22)):
        week_index = 3
    elif (date >= dt.date(2020, 10, 25)) and (date <= dt.date(2020, 10, 31)):
        week_index = 4
    return week_index


# created from qualitative review of most frequently occurring tags
NYT_THEME_TAG_SET = 1963
POLITICS = [9360836]
HEALTH = [9360852, 9360942]
ECONOMICS = [9360840, 9360859, 9360989]
SPORTS = [9361137]


def _has_one_of_tags(story_tags_ids: List[int], tag_ids_to_match: List[int]):
    for search_tag in tag_ids_to_match:
        if search_tag in story_tags_ids:
            return True
    return False


def nyt_theme(tags: List) -> Dict:
    nyt_tag_ids = [t['tags_id'] for t in tags if t['tag_sets_id'] == NYT_THEME_TAG_SET]
    return dict(
        nyt_theme_tag_ids=nyt_tag_ids,
        is_politics=_has_one_of_tags(nyt_tag_ids, POLITICS),
        is_health=_has_one_of_tags(nyt_tag_ids, HEALTH),
        is_economics=_has_one_of_tags(nyt_tag_ids, ECONOMICS),
        is_sports=_has_one_of_tags(nyt_tag_ids, SPORTS),
    )


def all_links(sentences: List[str]) -> List[Dict]:
    data = []
    for sentence_index, s in enumerate(sentences):
        soup = BeautifulSoup(s, features="lxml")
        links = soup.find_all('a', attrs={'href': re.compile("^https?://")})
        for link_index, a in enumerate(links):
            data.append(dict(
                link_id="{}-{}".format(sentence_index, link_index),  # so we a unique id for this link
                #sentence_number=sentence_index,
                #link_number=link_index,
                link_text=a.text,
                sentence=s,
                target_url=a['href'],
                target_domain=get_canonical_mediacloud_domain(a['href'])
            ))
    return data