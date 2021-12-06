import re
import tldextract
from typing import List

SEARCH_ENGINE_DOMAINS = ['google.com', 'bing.com', 'duckduckgo.com', 'baidu.com']

# domain names of most linked to platforms
PLATFORM_DOMAINS = [
    'facebook.com', 'fb.me', 'fb.com', 'messenger.com', 'youtube.com', 'instagram.com', 'linkedin.com', 'pinterest.com',
    'twitter.com', 'whatsapp.com', 'wechat.com', 'tiktok.com', 'qq.com', 'weibo.com', 'reddit.com', 'snapchat.com',
    'bit.ly', 'youtu.be'
]

# official websites run by government entities
GOV_DOMAIN_SUFFIXES = [
    '.gov.ph', '.gov', '.int'
]
GOV_DOMAINS = ['un.org', 'cdc.gov', 'worldbank.org']

# universities and such
EDUCATIONAL_DOMAINS_SUFFIXES = [
    '.edu', '.edu.ph'
]

countries = ['IND', 'GBR', 'KEN', 'ZAF', 'AUS', 'PHL', 'USA']


def has_country_suffix(domain: str, country_alpha3: str) -> bool:
    # https://en.wikipedia.org/wiki/Country_code_top-level_domain
    if country_alpha3 == 'IN':
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
    for suffix in suffixes:
        if domain.endswith(suffix):
            return True
    return False


def is_government_domain(domain: str) -> bool:
    return _domain_ends_with(domain, GOV_DOMAIN_SUFFIXES) or (domain in GOV_DOMAINS)


def is_educational_domain(domain: str) -> bool:
    return _domain_ends_with(domain, EDUCATIONAL_DOMAINS_SUFFIXES)


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
