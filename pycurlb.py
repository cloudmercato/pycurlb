#!/usr/bin/env python
"""
Python cURL benchmark - Get info about connection
"""
import sys
import argparse
import json
from io import BytesIO
from shutil import copyfileobj

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
        self.response_buffer = BytesIO()
        self.request_buffer = BytesIO()

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

    def perform(self, url, verbose=False, insecure=True, method=None, compressed=False,
                connect_timeout=300, connect_timeout_ms=None, data=None):
        self.curl.setopt(self.curl.URL, url)
        self.curl.setopt(self.curl.CUSTOMREQUEST, method)
        self.curl.setopt(self.curl.WRITEDATA, self.response_buffer)
        self.curl.setopt(self.curl.VERBOSE, verbose)
        self.curl.setopt(self.curl.SSL_VERIFYPEER, insecure)
        self.curl.setopt(self.curl.CONNECTTIMEOUT, connect_timeout)
        if connect_timeout_ms is not None:
            self.curl.setopt(self.curl.CONNECTTIMEOUT_MS, connect_timeout_ms)
        if compressed:
            self.curl.setopt(self.curl.ACCEPT_ENCODING, "gzip,deflate")
        if data is not None:
            self.request_buffer.write(data.encode())
            self.request_buffer.seek(0)
            self.curl.setopt(self.curl.UPLOAD, True)
            self.curl.setopt(self.curl.READFUNCTION, self.request_buffer.read)
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
                        help="Request compressed response.")
    parser.add_argument('--connect-timeout', default=300, type=int,
                        help="Maximum time allowed for connection in seconds.")
    parser.add_argument('--connect-timeout-ms', default=None, type=int,
                        help="Maximum time allowed for connection in milliseconds.")
    parser.add_argument('-d', '--data', default=None,
                        help="HTTP POST data.")
    parser.add_argument('-k', '--insecure', action='store_false',
                        help="Allow insecure server connections when using SSL.")
    parser.add_argument('-X', '--request',
                        help="Specify request command to use.")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="Make the operation more talkative.")
    parser.add_argument('-V', '--version', action='store_const', const=get_version,
                        default=None,
                        help="Show version number and quit.")
    parser.add_argument('-w', '--write-out', default=None,
                        help="Write request output to specified file.")
    args = parser.parse_args()
    # Meta
    if args.version is not None:
        sys.stdout.write(args.version())
        sys.stdout.write('\n')
        sys.exit(0)
    # Perform
    curler = Curler()
    info = curler.perform(
        compressed=args.compressed,
        connect_timeout=args.connect_timeout,
        connect_timeout_ms=args.connect_timeout_ms,
        data=args.data,
        insecure=args.insecure,
        method=args.request,
        url=args.url,
        verbose=args.verbose,
    )
    curler.close()
    # Print
    sys.stdout.write(json.dumps(info, indent=2, sort_keys=True))
    if args.write_out is not None:
        curler.response_buffer.seek(0)
        with open(args.write_out, 'wb') as dst_file:
            copyfileobj(curler.response_buffer, dst_file)

if __name__ == '__main__':
    main()
