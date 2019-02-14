import sys
import argparse
import json
from io import BytesIO

import pycurl

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

    def perform(self, url, verbose=False, insecure=True, method=None):
        self.curl.setopt(self.curl.URL, url)
        self.curl.setopt(self.curl.WRITEDATA, self.buffer)
        self.curl.setopt(self.curl.VERBOSE, verbose)
        self.curl.setopt(self.curl.SSL_VERIFYPEER, insecure)
        self.curl.perform()
        return self._extract_info()

    def close(self):
        self.curl.close()


def main():
    # Argparse
    parser = argparse.ArgumentParser(description="Get statistics from curl request")
    parser.add_argument('url')
    parser.add_argument('-k', '--insecure', action='store_false')
    parser.add_argument('-X', '--request')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    # Perform
    curler = Curler()
    info = curler.perform(
        method=args.request,
        url=args.url,
        verbose=args.verbose,
        insecure=args.insecure,
    )
    curler.close()
    # Print
    sys.stdout.write(json.dumps(info, indent=2, sort_keys=True))

if __name__ == '__main__':
    main()
