import unittest
import json
import os
from typing import Dict

import analyzer.analysis as analysis

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

test_fixture_dir = os.path.join(base_dir, "analyzer", "test", "fixtures")


def _load_fixture_json(file_name: str) -> Dict:
    with open(os.path.join(test_fixture_dir, file_name)) as f:
        story = json.load(f)
    return story


class TestAll(unittest.TestCase):

    def test_extract_content(self):
        story = _load_fixture_json("1514007166.json")
        results = analysis.extract_content(story['raw_first_download_file'])
        assert '<html><body><div><header' in results

    def test_remove_non_link_tags(self):
        story = _load_fixture_json("1514007166.json")
        results = analysis.remove_non_link_tags(story['content'])
        assert '<html><body><div><header' not in results

    def test_sentence_tokenization(self):
        story = _load_fixture_json("1514007166.json")
        results = analysis.sentence_tokenization(story['new_content'])
        assert len(results) == 8

    def test_all_links(self):
        story = _load_fixture_json("1514007166.json")
        results = analysis.all_links(story['sentences'])
        assert len(results) == 1
        assert results[0]['target_domain'] == "kenya-today.com"

    def test_country_alpha3(self):
        story = _load_fixture_json("1514007166.json")
        results = analysis.country_alpha3(story['media_id'])
        assert results == 'KEN'

    def test_study_week_index(self):
        story = _load_fixture_json("1514007166.json")
        results = analysis.study_week_index(story['publish_date'])
        assert results == 1

    def test_nyt_theme(self):
        story = _load_fixture_json("1514007166.json")
        results = analysis.nyt_theme(story['story_tags'])
        assert 'nyt_theme_tag_ids' in results
        assert len(results['nyt_theme_tag_ids']) == 1
        assert results['is_politics'] is True
        assert results['is_health'] is False
        assert results['is_economics'] is False


if __name__ == "__main__":
    unittest.main()
