import unittest
import json
import os
from typing import Dict

import analyzer.stages as stages

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

test_fixture_dir = os.path.join(base_dir, "analyzer", "test", "fixtures")


def _load_fixture_json(file_name: str) -> Dict:
    with open(os.path.join(test_fixture_dir, file_name)) as f:
        story = json.load(f)
    return story


class TestReadabilityStage(unittest.TestCase):

    def test_readability_stage(self):
        stage = stages.ReadabilityStage()
        story = _load_fixture_json("1514007166.json")
        results = stage.process(story)
        assert 'content' in results
        assert '<html><body><div><header' in results['content']


class TestRemoveTagsExceptLinksStage(unittest.TestCase):

    def test_remove_tags_stage(self):
        stage = stages.RemoveTagsExceptLinksStage()
        story = _load_fixture_json("1514007166.json")
        results = stage.process(story)
        assert 'new_content' in results
        assert '<html><body><div><header' not in results['new_content']


class TestSentenceTokenizationStageStage(unittest.TestCase):

    def test_sentences_stage(self):
        stage = stages.SentenceTokenizationStage()
        story = _load_fixture_json("1514007166.json")
        results = stage.process(story)
        assert 'sentences' in results
        assert len(results['sentences']) == 8


class TestSentenceLinkStage(unittest.TestCase):

    def test_sentences_stage(self):
        stage = stages.SentenceLinkStage()
        story = _load_fixture_json("1514007166.json")
        results = stage.process(story)
        assert 'links' in results
        assert len(results['links']) == 1
        assert results['links'][0]['target_domain'] == "kenya-today.com"


class TestNationalCountryCollectionStage(unittest.TestCase):

    def test_country_for_media(self):
        stage = stages.NationalCountryCollectionStage()
        story = _load_fixture_json("1514007166.json")
        results = stage.process(story)
        assert 'country' in results
        assert results['country'] == 'KEN'


class TestStudyWeekIndexStage(unittest.TestCase):

    def test_country_for_media(self):
        stage = stages.StudyWeekIndexStage()
        story = _load_fixture_json("1514007166.json")
        results = stage.process(story)
        assert 'week_number' in results
        assert results['week_number'] == 1


class TestNytThemeTagsStage(unittest.TestCase):

    def test_country_for_media(self):
        stage = stages.NytThemeTagsStage()
        story = _load_fixture_json("1514007166.json")
        results = stage.process(story)
        assert 'nyt_theme_tag_ids' in results
        assert len(results['nyt_theme_tag_ids']) == 1
        assert results['is_politics'] is True
        assert results['is_health'] is False
        assert results['is_economics'] is False


if __name__ == "__main__":
    unittest.main()
