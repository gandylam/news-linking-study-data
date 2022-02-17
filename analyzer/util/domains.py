import re
import tldextract
from typing import List
import os
import pandas as pd

from analyzer import data_dir, COUNTRIES

SEARCH_ENGINE_DOMAINS = ['google.com', 'bing.com', 'duckduckgo.com', 'baidu.com']

# official websites run by government entities
GOV_DOMAINS = ['un.org', 'worldbank.org']

# universities and such
EDUCATIONAL_DOMAINS_SUFFIXES = {
    'global': '.edu',
    'PHL': '.edu.ph',
}

suffixes_df = pd.read_csv(os.path.join(data_dir, 'country-domain-suffixes.csv'))
gov_suffixes = suffixes_df[suffixes_df['category'] == 'GOV'].groupby('country_alpha3')
edu_suffixes = suffixes_df[suffixes_df['category'] == 'EDU'].groupby('country_alpha3')
tld_suffixes = suffixes_df[suffixes_df['category'] == 'TLD'].groupby('country_alpha3')

platform_domains = [l.strip().lower() for l in open(os.path.join(data_dir, 'platform-domains.txt')).readlines()]

# load up manually coded domain categories
manual_domain_category_lookups = {}  # Dict[country, Dict[domain,category]]
for c in COUNTRIES:
    lookup = {}
    df = pd.read_csv(os.path.join(data_dir, "domain-categories-{}.csv".format(c)))
    for idx, row in df.iterrows():
        lookup[row['Id']] = row['Category']
    manual_domain_category_lookups[c] = lookup


def get_manual_category(country: str, domain: str) -> str:
    return manual_domain_category_lookups[country].get(domain, None)


def is_platform_domain(domain: str) -> bool:
    return domain.lower() in platform_domains


def has_country_suffix(domain: str, country_alpha3: str) -> bool:
    # https://en.wikipedia.org/wiki/Country_code_top-level_domain
    if country_alpha3 == 'IND':
        return _domain_ends_with(domain, ['.in'])
    elif country_alpha3 == 'GBR':
        return _domain_ends_with(domain, ['.uk', '.ac', '.bm', '.fk', '.gi', '.gs', '.ky', '.ms', '.pn', '.sh', '.tc', '.vg'])
    elif country_alpha3 == 'KEN':
        return _domain_ends_with(domain, ['.ke'])
    elif country_alpha3 == 'ZAF':
        return _domain_ends_with(domain, ['.za'])
    elif country_alpha3 == 'AUS':
        return _domain_ends_with(domain, ['.au', '.oz.au', '.oz'])
    elif country_alpha3 == 'PHL':
        return _domain_ends_with(domain, ['.ph'])
    elif country_alpha3 == 'USA':
        return _domain_ends_with(domain, ['.us', '.as', '.gu', '.mp', '.pr', '.vi'])
    return False


def _domain_ends_with(domain: str, suffixes: List) -> bool:
    # here we sort from longest to shortest in order to make sure subdomains get caught first
    for suffix in sorted(suffixes, key=len, reverse=True):
        if domain.endswith(suffix):
            return True
    return False


def is_government_domain(domain: str, country: str) -> bool:
    country_gov_suffixes = list(gov_suffixes.get_group(country)['suffix'])
    return _domain_ends_with(domain, country_gov_suffixes) or (domain in GOV_DOMAINS)


def is_educational_domain(domain: str, country: str) -> bool:
    country_edu_suffixes = list(edu_suffixes.get_group(country)['suffix'])
    return _domain_ends_with(domain, country_edu_suffixes)


# by James O'Toole (Media Cloud)
def get_canonical_mediacloud_domain(url:str) -> str:
    parsed_domain = tldextract.extract(url)

    is_blogging_subdomain = re.search(
        r'\.go\.com|\.wordpress\.com|\.blogspot\.|\.livejournal\.com|\.privet\.ru|\.wikia\.com'
        r'|\.24open\.ru|\.patch\.com|\.tumblr\.com|\.github\.io|\.typepad\.com'
        r'|\.squarespace\.com|\.substack\.com|\.iheart\.com|\.ampproject\.org|\.mail\.ru|\.wixsite\.com'
        r'|\.medium.com|\.free\.fr|\.list-manage\.com|\.over-blog\.com|\.weebly\.com|\.typeform\.com'
        r'|\.nationbuilder\.com|\.tripod\.com|\.insanejournal\.com|\.cloudfront\.net|\.wpengine\.com'
        r'|\.noblogs\.org|\.formstack\.com|\.altervista\.org|\.home\.blog|\.kinja\.com|\.sagepub\.com'
        r'|\.ning\.com|\.hypotheses\.org|\.narod\.ru|\.submittable\.com|\.smalltownpapers\.com'
        r'|\.herokuapp\.com|\.newsvine\.com|\.newsmemory\.com|\.beforeitsnews\.com|\.jimdo\.com'
        r'|\.wickedlocal\.com|\.radio\.com|\.stackexchange\.com|\.buzzsprout\.com'
        r'|\.appspot\.com|\.simplecast\.com|\.fc2\.com|\.podomatic\.com|\.azurewebsites\.|\.sharepoint\.com'
        r'|\.windows\.net|\.wix\.com|\.googleblog\.com|\.hubpages\.com|\.gitlab\.io|\.blogs\.com'
        r'|\.shinyapps\.io', url, re.I)

    is_relative_path = re.search(r'bizjournals\.com|stuff\.co\.nz', url, re.I)

    if is_blogging_subdomain:
        canonical_domain = parsed_domain.subdomain.lower() + '.' + parsed_domain.registered_domain.lower()
    elif is_relative_path:
        canonical_domain = parsed_domain.registered_domain.lower() + '/' + url + url.split('/')[3]
    else:
        canonical_domain = parsed_domain.registered_domain.lower()

    if 'cdn.ampproject.org' in canonical_domain:
        canonical_domain = canonical_domain.replace('.cdn.ampproject.org', '').replace('amp-', '').replace('/',
                                                                                                           '').replace(
            '--', '-')
        last_dash_index = canonical_domain.rfind('-')
        canonical_domain = canonical_domain[:last_dash_index] + '.' + canonical_domain[last_dash_index + 1:]

    return canonical_domain
