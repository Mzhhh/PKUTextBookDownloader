import re, json
import requests
from bs4 import BeautifulSoup
from urllib import parse
from collections import OrderedDict

URLKW_DICT = OrderedDict([
    ('objID', 'txtFileID'),
    ('metaId', 'txtMetaId'),
    ('OrgId', 'txtOrgIdentifier'),
    ('Ip', None),
    ('scale', None),
    ('width', None),
    ('height', None),
    ('pageid', None),
    ('ServiceType', None),
    ('scaleType', None),
    ('OrWidth', 'pagesWidth'),
    ('OrHeight', 'pagesHeight'),
    ('testres', 'txtTestRes'),
    ('debug', 'txtDebug'),
    ('SessionId', 'sessionid'),
    ('UserName', 'txtuserName'),
    ('cult', 'txtCultureName')
])

DEFAULT_DICT = {
    'Ip' : 'undefined',
    'scale': None,
    'scaleType': 1,
    'ServiceType': 'Imagepage'
}
URLRIGHT_ID = 'urlrights'
NUMPAGES_ID = 'TotalCount'
VIEWTIME_ID = 'txtOnlineViewTime'
PAGEID_KW = 'pageid'
PAGE_PATH= r'OnLineReader/command/imagepage.ashx'


def page_url_iter(meta_url, **kwargs):
    '''
    Generate the url corresponding to all the pages
    '''
    r = get_response(meta_url)
    bs = BeautifulSoup(r.text, features='lxml')
    num_pages = int(extract_fields(bs, NUMPAGES_ID, True))
    title = re.search('[<《](.*?)[》>]', bs.find('title').text)[1]
    
    decoded_fields = modify_decoded_dict(extract_fields(bs, URLKW_DICT), **kwargs)
    default_fields = DEFAULT_DICT
    viewtime = extract_fields(bs, VIEWTIME_ID)
    validation_str = extract_fields(bs, URLRIGHT_ID).replace(' ', '%'+viewtime)
    
    url_prefix = page_hostname(meta_url)
    query_fields = {**decoded_fields, **default_fields}
    def _page_url_iter():
        for i in range(1, num_pages+1):
            query_fields[PAGEID_KW] = str(i)
            query_str = parse.urlencode(query_fields)
            yield i, (url_prefix + query_str + '&' + validation_str)
    return (title, num_pages), _page_url_iter()


def get_response(meta_url):
    '''
    Get response from the url
    '''
    r = requests.get(meta_url)
    if r.status_code != 200:
        raise Exception('Bad Access')
    r.encoding = r.apparent_encoding
    return r


def extract_fields(bs, query, as_text=False):
    '''
    Extract useful information from the response
    '''
    if isinstance(query, dict):
        return {url_kw:from_soup(bs, html_kw) for url_kw, html_kw in query.items()}
    elif isinstance(query, str):
        if not as_text:
            return bs.find(id=query)['value']
        else:
            return bs.find(id=query).text


def from_soup(soup, key):
    search_result = soup.find(id=key)
    if not search_result:
        return None
    else:
        return search_result.get('value', '').lower()


def page_hostname(meta_url):
    '''
    Generate the url prefix of the images
    '''
    meta = parse.urlsplit(meta_url)
    scheme, netloc = meta.scheme, meta.netloc
    return parse.ParseResult(scheme, netloc, PAGE_PATH, '', '', '').geturl() + '?'


def modify_decoded_dict(decoded_fields, target_width=1000, target_scale=None, **kwargs):
    if not target_width and target_scale:
        DEFAULT_DICT['scale'] = target_scale
    else:
        DEFAULT_DICT['scale'] = target_width / float(decoded_fields['OrWidth'])
    decoded_fields['width'] = str(DEFAULT_DICT['scale'] * float(decoded_fields['OrWidth']))
    decoded_fields['height'] = str(DEFAULT_DICT['scale'] * float(decoded_fields['OrHeight']))
    decoded_fields['cult'] = decoded_fields['cult'].upper()
    return decoded_fields