#!/usr/bin/env python
"""
https://stem.torproject.org/tutorials/to_russia_with_love.html

Usage:
  russian-tor-exit-node [<tor>] [--color] [--geoipfile=</path/to/file>]
  russian-tor-exit-node -h | --help
  russion-tor-exit-node --version

Dependencies:

- tor (packaged and standalone executables work)
- pip install stem
- pip install PySocks
- pip install docopt
  : parse options
- pip install colorama
  : cross-platform support for ANSI colors
- [optional] sudo apt-get tor-geoipdb
  : if tor is bundled without geoip files; --geoipfile=/usr/share/tor/geoip
"""
import sys
from contextlib import closing

import colorama  # $ pip install colorama
import docopt  # $ pip install docopt
import socks  # $ pip install PySocks
import stem.process  # $ pip install stem
from sockshandler import SocksiPyHandler  # see pysocks repository
from stem.util import term

try:
    import urllib2
except ImportError: # Python 3
    import urllib.request as urllib2


args = docopt.docopt(__doc__, version='0.2')
colorama.init(strip=not (sys.stdout.isatty() or args['--color']))

tor_cmd = args['<tor>'] or 'tor'
socks_port = 9050
config = dict(SocksPort=str(socks_port), ExitNodes='{dk,ru,ua}')
if args['--geoipfile']:
    config.update(GeoIPFile=args['--geoipfile'], GeoIPv6File=args['--geoipfile']+'6')


def query(url, opener=urllib2.build_opener(
        SocksiPyHandler(socks.PROXY_TYPE_SOCKS5, "localhost", socks_port))):
  try:
      with closing(opener.open(url)) as r:
          return r.read().decode('ascii')
  except EnvironmentError as e:
    return "Unable to reach %s: %s" % (url, e)

try:
    print(term.format("\nChecking our endpoint:\n", term.Attr.BOLD))
    print(term.format(query("https://icanhazip.com"), term.Color.BLUE))
except Exception as e:
    print(e)
