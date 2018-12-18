#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
bitlyfy.py - Shorten or expand URL via the Bitly API (dev.bitly.com)
"""

import argparse, os, sys, netrc
import requests
from urllib.parse import quote as percent_encode
from requests.exceptions import ConnectionError, SSLError

DESCRIPTION = '''
Shorten or expand URL via the Bitly API
'''
API = 'https://api-ssl.bitly.com'
SHORTEN = '/v3/shorten'
EXPAND = '/v3/expand'
ACCESS_TOKEN_FILE = '.netrc'
HOST = 'api-ssl.bitly.com'

def bitly_url(bitly_resp, expand_url=False, url_type='url'):
    if expand_url:
        bitly_resp, url_type = bitly_resp['expand'][0], 'long_url'
    url = bitly_resp[url_type]
    return url

def url_from_bitly_req(response, expand_url=False):
    resp = response.json()
    invalid_bitly_request = (resp['status_code'] != 200)
    if invalid_bitly_request:
        error_msg = 'Bitly query error: %s' % resp['status_txt']
        return error_msg
    url = bitly_url(resp['data'], expand_url=expand_url)
    return url

def make_bitly_get_req(args, link=SHORTEN, url_type='longUrl'):
    if args.expand:
        link, url_type = EXPAND, 'shortUrl'
    if args.access_token:
        access_token = args.access_token
    else:
        token_file = os.path.join(os.environ['HOME'], ACCESS_TOKEN_FILE)
        try:
            _, _, access_token = netrc.netrc(token_file).authenticators(HOST)
        except (FileNotFoundError, TypeError):
            raise SystemExit('Access token not found: %s' % token_file)
    url = percent_encode(args.URL, safe=':/')
    params = {'access_token': access_token, url_type: url,
              'format': 'json'}  # JSON is the default response format
    query = API + link
    return query, params

def get_bitly_url(args):
    query, params = make_bitly_get_req(args)
    r = requests.get(query, params=params)
    return url_from_bitly_req(r, expand_url=args.expand)

def bitlyfy(args):
    try:
        return get_bitly_url(args)
    except (ConnectionError, SSLError):
        return 'Failed to establish network connection'

def get_arguments():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('URL', type=str, help='URL to shorten or expand (with -e)')
    parser.add_argument('-a', '--access_token', type=str,
                        help='''Bitly access token; if this option is omitted,
                             the access token will be read from the machine entry "%s"
                             in the netrc file $HOME/%s''' % (HOST, ACCESS_TOKEN_FILE))
    parser.add_argument('-e', '--expand', action='store_true',
                        help='Expand (short) URL to long URL')
    return parser

def main():
    args = get_arguments().parse_args()
    print(bitlyfy(args))

if __name__ == '__main__':
    sys.exit(main())
