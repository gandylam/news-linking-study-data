import re
from readability import Document
from bs4 import BeautifulSoup
from typing import Dict, List
import spacy
import datetime as dt
import dateparser

from analyzer.util.domains import get_canonical_mediacloud_domain
import analyzer.util.collections as collections

#nlp = None
nlp = spacy.load('en_core_web_sm')


class Stage(object):

    def process(self, story) -> Dict:
        raise NotImplementedError("Subclasses should implement this!")


class ReadabilityStage(Stage):

    def process(self, story) -> Dict:
        story_html = story['raw_first_download_file']
        doc = Document(story_html)
        content = doc.summary()
        return dict(content=content)


class RemoveTagsExceptLinksStage(Stage):

    # https://stackoverflow.com/questions/44078/strip-all-html-tags-except-links
    TAGS_EXCEPT_LINKS_PATTERN = r"<(?!\/?a(?=>|\s.*>))\/?.*?>"

    def process(self, story) -> Dict:
        story_html = story['content']
        new_content = re.sub(RemoveTagsExceptLinksStage.TAGS_EXCEPT_LINKS_PATTERN, "", story_html)
        return dict(new_content=new_content)


class SentenceTokenizationStage(Stage):

    def process(self, story) -> Dict:
        story_content = story['new_content']
        doc = nlp(story_content)
        sentences = [str(s) for s in doc.sents]
        sentences = [s.strip() for s in sentences if len(s.strip()) > 0]
        return dict(sentences=sentences)


class NationalCountryCollectionStage(Stage):

    def process(self, story) -> Dict:
        media_id = story['media_id']
        country_alpha3 = collections.country_for_media(media_id)
        return dict(country=country_alpha3)


class StudyWeekIndexStage(Stage):

    def process(self, story) -> Dict:
        date_str = story['publish_date']
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
        return dict(week_number=week_index)


class NytThemeTagsStage(Stage):

    NYT_THEME_TAG_SET = 1963

    # created from qualitative review of most frequently occurring tags
    POLITICS = [9360836]
    HEALTH = [9360852, 9360942]
    ECONOMICS = [9360840, 9360859, 9360989]

    def _has_one_of_tags(self, story_tags_ids: List[int], tag_ids_to_match: List[int]):
        for search_tag in tag_ids_to_match:
            if search_tag in story_tags_ids:
                return True
        return False

    def process(self, story) -> Dict:
        tags = story['story_tags']
        nyt_tag_ids = [t['tags_id'] for t in tags if t['tag_sets_id'] == NytThemeTagsStage.NYT_THEME_TAG_SET]
        return dict(
            nyt_theme_tag_ids=nyt_tag_ids,
            is_politics=self._has_one_of_tags(nyt_tag_ids, self.POLITICS),
            is_health=self._has_one_of_tags(nyt_tag_ids, self.HEALTH),
            is_economics=self._has_one_of_tags(nyt_tag_ids, self.ECONOMICS),
        )


class SentenceLinkStage(Stage):

    def process(self, story) -> Dict:
        sentences = story['sentences']
        data = []
        for sentence_index, s in enumerate(sentences):
            soup = BeautifulSoup(s, features="lxml")
            links = soup.find_all('a', attrs={'href': re.compile("^https?://")})
            for link_index, a in enumerate(links):
                source_domain = get_canonical_mediacloud_domain(story['url'])
                target_domain = get_canonical_mediacloud_domain(a['href'])
                data.append(dict(
                    link_id="{}-{}-{}".format(story['stories_id'], sentence_index, link_index),  # so we a unique id for this link
                    #sentence_number=sentence_index,
                    #link_number=link_index,
                    source_stories_id=story['stories_id'],
                    publication_date=story['publish_date'],
                    sentence=s,
                    source_url=story['url'],
                    source_domain=source_domain,
                    link_text=a.text,
                    target_url=a['href'],
                    target_domain=target_domain,
                    source_country=story['country'],
                    week_number=story['week_number'],
                    source_nyt_themes=story['nyt_theme_tag_ids'],
                    source_story_is_politics=story['is_politics'],
                    source_story_is_health=story['is_health'],
                    source_story_is_economics=story['is_economics'],
                    source_story_sentence_count=len(sentences),
                    is_self_link=(source_domain == target_domain),
                ))
        return dict(links=data)
