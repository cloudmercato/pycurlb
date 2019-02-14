=====================
Python cURL benchmark
=====================

pycurlb is a wrapper around libcurl and pycurl allowing to retrieve info about connections.

Install
=======

This project works only with Python 3.

::

  pip install pycurlb

Usage
=====

In Python
---------

::

  from pycurlb import Curler
  
  curler = Curler()
  info = curler.perform('http://example.com')
  print(info)
  

In Shell
--------

::

  curlb http://example.com
  
  {
    "appconnect_time": 0.0,
    "connect_time": 0.20492,
    "content_length_download": 1270.0,
    "content_length_upload": -1.0,
    "content_type": "text/html; charset=UTF-8",
    "effective_url": "http://example.com/",
    "ftp_entry_path": null,
    "header_size": 344,
    "http_code": 200,
    "http_connectcode": 0,
    "local_ip": "10.211.55.3",
    "local_port": 35040,
    "namelookup_time": 0.02877,
    "num_connects": 1,
    "os_errno": 0,
    "pretransfer_time": 0.20498700000000003,
    "primary_ip": "93.184.216.34",
    "primary_port": 80,
    "redirect_count": 0,
    "redirect_time": 0.0,
    "redirect_url": null,
    "request_size": 141,
    "size_download": 1270.0,
    "size_upload": 0.0,
    "speed_download": 3478.0,
    "speed_upload": 0.0,
    "ssl_engines": [],
    "ssl_verifyresult": 0,
    "starttransfer_time": 0.364974,
    "total_time": 0.36507199999999995
  }
  
We try to keep the same options than the original ``curl`` comamnd.
