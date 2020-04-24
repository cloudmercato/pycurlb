#!/usr/bin/env python
"""
Python cURL benchmark - Get info about connection
"""
import sys
import argparse
import json
from io import BytesIO
from shutil import copyfileobj

try:
    import pycurl
except ImportError:
    pycurl = None

VERSION = (0, 2, 2)
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
    'scheme',
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
            except TypeError:
                pass
        return info

    def perform(self, url, verbose=False, insecure=True, method=None, compressed=False,
                connect_timeout=300, connect_timeout_ms=None, data=None, headers=None,
                http10=False, http11=False, http2=False,
                user=None, user_agent=None, max_time=0, max_time_ms=None, cookie=None,
                cookie_jar=None, get=False, ignore_content_length=False,
                expect100_timeout_ms=None, ip_resolve=None):
        ip_resolve = ip_resolve or pycurl.IPRESOLVE_WHATEVER
        info = {
            'method': method or 'GET',
            'max_time': max_time,
            'connect_timeout': connect_timeout,
            'compressed': compressed,
        }
        self.curl.setopt(self.curl.URL, url)
        self.curl.setopt(self.curl.CUSTOMREQUEST, method)
        self.curl.setopt(self.curl.WRITEDATA, self.response_buffer)
        self.curl.setopt(self.curl.VERBOSE, verbose)
        self.curl.setopt(self.curl.SSL_VERIFYPEER, insecure)
        self.curl.setopt(self.curl.CONNECTTIMEOUT, connect_timeout)
        self.curl.setopt(self.curl.TIMEOUT, max_time)
        self.curl.setopt(self.curl.IPRESOLVE, ip_resolve)
        self.curl.setopt(self.curl.IGNORE_CONTENT_LENGTH, ignore_content_length)
        if expect100_timeout_ms:
            self.curl.setopt(self.curl.EXPECT_100_TIMEOUT_MS, expect100_timeout_ms)
        if cookie:
            self.curl.setopt(self.curl.COOKIE, cookie)
        if cookie_jar:
            self.curl.setopt(self.curl.COOKIEJAR, cookie_jar)
        if headers:
            self.curl.setopt(self.curl.HTTPHEADER, headers)
        if http10:
            self.curl.setopt(pycurl.HTTP_VERSION, self.curl.CURL_HTTP_VERSION_1_0)
        elif http11:
            self.curl.setopt(pycurl.HTTP_VERSION, self.curl.CURL_HTTP_VERSION_1_1)
        elif http2:
            self.curl.setopt(pycurl.HTTP_VERSION, self.curl.CURL_HTTP_VERSION_2_0)
        else:
            self.curl.setopt(pycurl.HTTP_VERSION, pycurl.CURL_HTTP_VERSION_NONE)
        if user_agent is not None:
            self.curl.setopt(self.curl.USERAGENT, user_agent)
        if user is not None:
            self.curl.setopt(self.curl.USERPWD, user_agent)
        if connect_timeout_ms is not None:
            self.curl.setopt(self.curl.CONNECTTIMEOUT_MS, connect_timeout_ms)
            info['connect_timeout'] = connect_timeout_ms / 1000
        if max_time_ms is not None:
            self.curl.setopt(self.curl.TIMEOUT_MS, max_time_ms)
            info['max_time'] = max_time_ms / 1000
        if compressed:
            self.curl.setopt(self.curl.ACCEPT_ENCODING, "gzip,deflate")
        if data is not None:
            self.request_buffer.write(data.encode())
            self.request_buffer.seek(0)
            self.curl.setopt(self.curl.UPLOAD, True)
            self.curl.setopt(self.curl.READFUNCTION, self.request_buffer.read)
        if get:
            self.curl.setopt(self.curl.HTTPGET, get)
        try:
            self.curl.perform()
        except pycurl.error:
            pass
        info.update(self._extract_info())
        return info

    def close(self):
        self.curl.close()


def get_version():
    version = 'pycurlb/%s %s' % (__version__, pycurl.version)
    return version


def main():
    # Argparse
    parser = argparse.ArgumentParser(
        prog='curlb',
        description="Get statistics from curl request"
    )
    parser.add_argument('url')
    parser.add_argument('--compressed', action='store_true',
                        help="Request compressed response.")
    parser.add_argument('--connect-timeout', default=300, type=int, metavar='<seconds>',
                        help="Maximum time allowed for connection in seconds.")
    parser.add_argument('--connect-timeout-ms', default=None, type=int, metavar='<ms>',
                        help="Maximum time allowed for connection in milliseconds.")
    parser.add_argument('-b', '--cookie', default=None, metavar='<data>',
                        help="Send cookies from string/file")
    parser.add_argument('-c', '--cookie-jar', default=None, metavar='<filename>',
                        help="Write cookies to <filename> after operation")
    parser.add_argument('--expect100-timeout', default=None, metavar='<seconds>',
                        help="How long to wait for 100-continue in seconds.")
    parser.add_argument('--expect100-timeout-ms', default=None, metavar='<ms>',
                        help="How long to wait for 100-continue in milliseconds.")
    parser.add_argument('-d', '--data', default=None, metavar='<data>',
                        help="HTTP POST data.")
    parser.add_argument('-g', '--get', action='store_true',
                        help="Put the post data in the URL and use GET")
    parser.add_argument('-H', '--header', default=[], nargs='*', metavar='<header/@file>',
                        help="Pass custom header(s) to server.")
    parser.add_argument('-0', '--http1.0', action='store_true', dest="http10",
                        help="Use HTTP 1.0")
    parser.add_argument('--http1.1', action='store_true', dest="http11",
                        help="Use HTTP 1.1")
    parser.add_argument('--http2', action='store_true', dest="http2",
                        help="Use HTTP 2")
    parser.add_argument('--ignore-content-length', action='store_true',
                        help="Allow insecure server connections when using SSL.")
    parser.add_argument('-k', '--insecure', action='store_false',
                        help="Allow insecure server connections when using SSL.")
    parser.add_argument('-4', '--ipv4', default=pycurl.IPRESOLVE_WHATEVER, action='store_const',
                        const=pycurl.IPRESOLVE_V4, dest="ip_resolve",
                        help="Resolve names to IPv4 addresses.")
    parser.add_argument('-6', '--ipv6', action='store_const', const=pycurl.IPRESOLVE_V6,
                        dest="ip_resolve", help="Resolve names to IPv6 addresses.")
    parser.add_argument('-m', '--max-time', default=0, type=int, metavar='<seconds>',
                        help="Maximum time allowed for the transfer in seconds.")
    parser.add_argument('--max-time-ms', default=None, type=int, metavar='<ms>',
                        help="Maximum time allowed for the transfer in milliseconds.")
    parser.add_argument('-o', '--output', default=None, metavar='<file>',
                        help="Write response output to specified file.")
    parser.add_argument('-X', '--request', metavar='<command>',
                        help="Specify request command to use.")
    parser.add_argument('-A', '--user-agent', default=None, metavar='<name>',
                        help="Send User-Agent to server.")
    parser.add_argument('-u', '--user', default=None, metavar='<user:password>',
                        help="<user:password> Server user and password")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="Make the operation more talkative.")
    parser.add_argument('-V', '--version', action='store_const', const=get_version,
                        default=None,
                        help="Show version number and quit.")
    args = parser.parse_args()
    # Meta
    if args.version is not None:
        sys.stdout.write(args.version())
        sys.stdout.write('\n')
        sys.exit(0)
    # Set headers
    headers = []
    for header in args.header:
        if header.startswith('@'):
            try:
                with open(header, 'r') as header_fd:
                    headers.extend(header_fd.readlines())
            except Exception as err:  # noqa
                sys.stderr.write("Warning: Failed to open %s: %s" % (header, err))
        else:
            headers.append(header)
    # Set misc
    if args.expect100_timeout_ms or args.expect100_timeout:
        expect100_timeout_ms = args.expect100_timeout_ms or args.expect100_timeout * 1000
    else:
        expect100_timeout_ms = None
    # Perform
    curler = Curler()
    info = curler.perform(
        compressed=args.compressed,
        connect_timeout=args.connect_timeout,
        connect_timeout_ms=args.connect_timeout_ms,
        cookie=args.cookie,
        cookie_jar=args.cookie_jar,
        expect100_timeout_ms=expect100_timeout_ms,
        data=args.data,
        get=args.get,
        headers=headers,
        ignore_content_length=args.ignore_content_length,
        insecure=args.insecure,
        ip_resolve=args.ip_resolve,
        max_time=args.max_time,
        max_time_ms=args.max_time_ms,
        method=args.request,
        url=args.url,
        user=args.user,
        user_agent=args.user_agent,
        verbose=args.verbose,
    )
    curler.close()
    # Print
    sys.stdout.write(json.dumps(info, indent=2, sort_keys=True))
    if args.output is not None:
        curler.response_buffer.seek(0)
        with open(args.output, 'wb') as dst_file:
            copyfileobj(curler.response_buffer, dst_file)

if __name__ == '__main__':
    main()
