import unittest

import analyzer.util.collections as collections


class TestMediaToNationalAlpha(unittest.TestCase):

    def test_media_kenya(self):
        media_id = 40852
        country = collections.country_for_media(media_id)
        assert country == 'KEN'

    def test_media_uk(self):
        media_id = 271
        country = collections.country_for_media(media_id)
        assert country == 'GBR'
