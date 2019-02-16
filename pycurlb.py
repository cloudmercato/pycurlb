#!/usr/bin/env python
"""
Python cURL benchmark - Get info about connection
"""
import sys
import argparse
import json
from io import BytesIO

import pycurl

VERSION = (0, 1, 0)
__version__ = '.'.join([str(i) for i in VERSION])
__author__ = "Anthony Monthe (ZuluPro)"
__email__ = 'amonthe@cloudspectator.com'
__url__ = 'https://github.com/cloudspectatordevelopment/pycurlb'


# https://curl.haxx.se/libcurl/c/curl_easy_getinfo.html
INFO_KEYS = [
    'content_type',
    'ftp_entry_path',
    'http_code',
    'http_connectcode',
    'http_version',
    'local_ip',
    'local_port',
    'num_connects',
    'redirect_count',
    'redirect_time',
    'ssl_verifyresult',
    'redirect_url',
    'primary_ip',
    'primary_port',
    'size_download',
    'size_upload',
    'header_size',
    'request_size',
    'speed_download',
    'speed_upload',
    'content_length_download',
    'content_length_upload',
    'appconnect_time',
    'connect_time',
    'namelookup_time',
    'pretransfer_time',
    'starttransfer_time',
    'total_time',
    'effective_url',
    'stderr',
    'stdout',
    'os_errno',
    'ssl_engines',
    'ssl_verifyresult',
    'proxy_ssl_verifyresult',
    'httpauth_avail',
    'proxyauth_avail',
    'filetime',
    'cookielist',
    'protocol',
    'certinfo',
    'condition_unmet',
]


class Curler:
    def __init__(self):
        self.curl = pycurl.Curl()
        self.buffer = BytesIO()

    def _extract_info(self):
        info = {}
        for key in INFO_KEYS:
            key_upper = key.upper()
            if not hasattr(self.curl, key_upper):
                continue
            attr = getattr(self.curl, key_upper)
            try:
                value = self.curl.getinfo(attr)
                info[key] = value
            except ValueError:
                pass
        return info

    def perform(self, url, verbose=False, insecure=True, method=None, compressed=False):
        self.curl.setopt(self.curl.URL, url)
        self.curl.setopt(self.curl.CUSTOMREQUEST, method)
        self.curl.setopt(self.curl.WRITEDATA, self.buffer)
        self.curl.setopt(self.curl.VERBOSE, verbose)
        self.curl.setopt(self.curl.SSL_VERIFYPEER, insecure)
        if compressed:
            self.curl.setopt(self.curl.ACCEPT_ENCODING, "gzip,deflate")
        # self.curl.setopt(self.curl.UPLOAD, True)
        # self.curl.setopt(self.curl.READFUNCTION, BytesIO(b'\n').read)
        # self.curl.setopt(self.curl.INFILESIZE, 0)
        self.curl.perform()
        return self._extract_info()

    def close(self):
        self.curl.close()


def get_version():
    version = 'pycurlb/%s %s' % (__version__, pycurl.version)
    return version


def main():
    # Argparse
    parser = argparse.ArgumentParser(description="Get statistics from curl request")
    parser.add_argument('url')
    parser.add_argument('--compressed', action='store_true',
                        help="Request compressed response")
    parser.add_argument('-k', '--insecure', action='store_false',
                        help="Allow insecure server connections when using SSL")
    parser.add_argument('-X', '--request',
                        help="Specify request command to use")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="Make the operation more talkative")
    parser.add_argument('-V', '--version', action='store_const', const=get_version,
                        default=None,
                        help="Show version number and quit")
    args = parser.parse_args()
    # Meta
    if args.version is not None:
        sys.stdout.write(args.version())
        sys.stdout.write('\n')
        sys.exit(0)
    # Perform
    curler = Curler()
    info = curler.perform(
        method=args.request,
        url=args.url,
        verbose=args.verbose,
        insecure=args.insecure,
        compressed=args.compressed,
    )
    curler.close()
    # Print
    sys.stdout.write(json.dumps(info, indent=2, sort_keys=True))

if __name__ == '__main__':
    main()
