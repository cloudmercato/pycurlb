import sys
import argparse
import json
from io import BytesIO

import pycurl

INFO_KEYS = [
    'content_type',
    'ftp_entry_path',
    'http_code',
    'http_connect',
    'http_version',
    'local_ip',
    'local_port',
    'num_connects',
    'num_redirects',
    'proxy_ssl_verify_result',
    'redirect_url',
    'remote_ip',
    'remote_port',
    'scheme',
    'size_download',
    'size_header',
    'size_request',
    'size_upload',
    'speed_download',
    'speed_upload',
    'ssl_verify_result',
    'time_appconnect',
    'time_connect',
    'time_namelookup',
    'time_pretransfer',
    'time_redirect',
    'time_starttransfer',
    'time_total',
    'url_effective',
    'stderr',
    'stdout',
]


class Curler:
    def __init__(self):
        self.curl = pycurl.Curl()
        self.buffer = BytesIO()

    def _extract_info(self):
        info = {}
        for key in INFO_KEYS:
            key_upper = key.upper()
            if hasattr(self.curl, key_upper):
                attr = getattr(self.curl, key_upper)
                try:
                    value = self.curl.getinfo(attr)
                    info[key] = value
                except ValueError:
                    pass
        return info

    def perform(self, url, verbose=False, method=None):
        self.curl.setopt(self.curl.URL, url)
        self.curl.setopt(self.curl.WRITEDATA, self.buffer)
        self.curl.setopt(self.curl.VERBOSE, verbose)
        self.curl.perform()
        # self.curl.close()
        return self._extract_info()


def main():
    # Argparse
    parser = argparse.ArgumentParser(description="Get statistics from curl request")
    parser.add_argument('url')
    parser.add_argument('-X', '--request')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    # Perform
    curler = Curler()
    info = curler.perform(
        method=args.request,
        url=args.url,
        verbose=args.verbose,
    )
    # Print
    sys.stdout.write(json.dumps(info, indent=2, sort_keys=True))

if __name__ == '__main__':
    main()
