import unittest

import analyzer.util.domains as domains


class TestCanonicalDomain(unittest.TestCase):

    def test_french_domain(self):
        test_url = "https://observers.france24.com/en/20190826-mexico-african-migrants-trapped-protest-journey"
        domain = domains.get_canonical_mediacloud_domain(test_url)
        assert domain == "france24.com"

    def test_org(self):
        test_url = "https://www.kpbs.org/news/2019/jul/09/migrants-cameroon-protest-immigration-process-tiju/"
        domain = domains.get_canonical_mediacloud_domain(test_url)
        assert domain == "kpbs.org"

    def test_hyphen(self):
        test_url = "https://www.kenya-today.com/media/moi-burial-confused-ruto-as-matiangi-declares-tuesday-a-public-holiday#comments"
        domain = domains.get_canonical_mediacloud_domain(test_url)
        assert domain == "kenya-today.com"


class TestDomains(unittest.TestCase):

    def test_is_platform(self):
        domain = 'facebook.com'
        assert domains.is_platform_domain(domain) is True

    def test_is_gov(self):
        domain = 'government.gov.ph'
        assert domains.is_government_domain(domain, 'PHL') is True

    def test_is_edu(self):
        domain = 'school.edu.au'
        assert domains.is_educational_domain(domain, 'AUS') is True

    def test_has_country_suffix(self):
        domain = 'awesome-stuff.in'
        assert domains.has_country_suffix(domain, 'IND') is True

    def test_get_manual_category(self):
        assert domains.get_manual_category('USA', 'cdc.gov') == 'Government'
        assert domains.get_manual_category('ZAF', 'cdc.gov') == 'Foreign Government'
        assert domains.get_manual_category('IND', 'mediacloud.org') is None
