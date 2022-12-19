#!/usr/bin/env python3

import curses
import json
import sys
import time
import platform
import os
import re
from argparse import ArgumentParser as AP

is_windows = lambda : platform.system().lower() == 'windows'
is_linux = lambda : platform.system().lower() == 'linux'


try:
    import zmq
except ImportError:
    print("zmq module not found")
    print()
    if is_linux():
        print("for debian-based linux do:")
        print("\tsudo apt install python3-zmq")
        print("for other linuxs do:")
        print("\tpip3 install --user zmq")
    else:
        print("install it with:")
        print("\tpip3 install --user zmq")
    sys.quit()

geo = None

try:
    import GeoIP
except ImportError:
    print("geoip module not found")
    print()
    if is_linux():
        print("for debian-based linux do:")
        print("\tsudo apt install python3-geoip")
        print("for other linuxs do:")
        print("\tpip3 install --user geoip")
        print("for other linuxs you are responsible for obtaining your owen geoip databases, glhf")
        time.sleep(1)
    else:
        print("install it with:")
        print("\tpip3 install --user geoip")
        print()
        print("press enter to continue without geoip")
        sys.stdin.read(1)
else:
    try:
        geoip_env_var = 'GEOIP_DB_FILE'
        if is_windows():
            geoip_default_db = '.\\GeoIP.dat'
        else:
            geoip_default_db = "/usr/share/GeoIP/GeoIP.dat"
        geoip_db_file = geoip_env_var in os.environ and os.environ[geoip_env_var] or geoip_default_db
        if not os.path.exists(geoip_db_file):
            print("no geoip database found at {}".format(geoip_db_file))
            print("you can override the path to it using the {} environmental variable".format(geoip_env_var))
            sys.quit()
        geo = GeoIP.open(geoip_db_file, GeoIP.GEOIP_STANDARD)
    except Exception as ex:
        print('failed to load geoip database: {}'.format(ex))
        time.sleep(1)

now = lambda : int(time.time()) * 1000


def ip_to_flag(ip):
    """
    convert an ip to a flag emoji
    """
    # bail if no geoip available
    if not geo:
        return ''
    # trim off excess ipv6 jizz
    ip = ip.replace("::ffff:", "")
    # get the country code
    cc = geo.country_code_by_addr(ip)
    # Unicode flag sequences are just country codes transposed into the REGIONAL
    # INDICATOR SYMBOL LETTER A ... Z range (U+1F1E6 ... U+1F1FF):
    flag = ''.join(chr(0x1f1e6 + ord(i) - ord('A')) for i in cc)
    return '({}) {}'.format(cc, flag)


class Monitor:

    _sample_size = 12
    filter = lambda x : True

    def __init__(self, url):
        self.data = dict()
        self._rpc_context = zmq.Context()
        self._rpc_socket = self._rpc_context.socket(zmq.DEALER)
        self._rpc_socket.setsockopt(zmq.CONNECT_TIMEOUT, 5000)
        self._rpc_socket.setsockopt(zmq.HANDSHAKE_IVL, 5000)
        self._rpc_socket.connect(url)

    def rpc(self, method):
        self._rpc_socket.send_multipart([method.encode(), b'lokinetmon'+method.encode()])
        if not self._rpc_socket.poll(timeout=50):
            return
        reply = self._rpc_socket.recv_multipart()
        if len(reply) >= 3 and reply[0:2] == [b'REPLY', b'lokinetmon'+method.encode()]:
            return reply[2].decode()

    def _close(self):
        self._rpc_socket.close(linger=0)

    def update_data(self):
        """update data from lokinet"""
        try:
            data = json.loads(self.rpc("llarp.status"))
            self.data = data['result']
        except:
            self.data = None
        return self.data is not None

    def _render_path(self, path, name):
        """render a path at current position"""
        #print("({}) ".format(name))
        #print("[tx:\t{}]\t[rx:\t{}]".format(
        #    self.speed_of(path['txRateCurrent']), self.speed_of(path['rxRateCurrent'])))
        pathstr = "me"
        for hop in path["hops"]:
            hopstr = hop['router'][:4]
            if 'ip' in hop:
                pathstr += ' -> {}'.format(hop['ip'].split(":")[3])

        print(pathstr)

        #print(" [{} ms latency]".format(path["intro"]["latency"]))
        #print(" [expires: {}]".format(self.time_to(path["expiresAt"])))
        #if path["expiresSoon"]:
        #    print("(expiring)")
        #elif path["expired"]:
        #    print("(expired)")

        print()

    @staticmethod
    def speed_of(rate):
        """turn int speed into string formatted"""
        units = ["b", "Kb", "Mb", "Gb"]
        idx = 0
        rate *= 8
        while rate > 1000 and idx < len(units):
            rate /= 1000.0
            idx += 1
        return "{} {}ps".format("%.2f" % rate, units[idx])
    @staticmethod
    def time_to(timestamp):
        """ return time until timestamp formatted"""
        if timestamp:
            unit = 'seconds'
            val = (timestamp - now()) / 1000.0
            if abs(val) > 60.0:
                val /= 60.0
                unit = 'minutes'
            if val < 0:
                return "{:.2f} {} ago".format(0-val, unit)
            else:
                return "in {:.2f} {}".format(val, unit)
        else:
            return 'never'

    def get_all_paths(self):
        """ yield all paths in current data """
        for key in self.data['services']:
            status = self.data['services'][key]
            for path in (status['paths'] or []):
                yield path
            for sess in (status['remoteSessions'] or []):
                for path in sess['paths']:
                    yield path
            for sess in (status['snodeSessions'] or []):
                for path in sess['paths']:
                    yield path

    def display_service(self, name, status):
        """display a service at current position"""
        
        print("service [{}]".format(name))
        build = status["buildStats"]
        ratio = build["success"] / (build["attempts"] or 1)
        print("build success: {} %".format(int(100 * ratio)))
        paths = status["paths"]
        print("paths: {}".format(len(paths)))
        for path in paths:
            if self.filter('localhost.loki'):
                self._render_path(path, "localhost.loki")
        for session in (status["remoteSessions"] or []):
            for path in session["paths"]:
                if self.filter(session["remoteIdentity"]):
                    self._render_path(
                        path, "[active] {}".format(session["currentConvoTag"])
                    )
        for session in (status["snodeSessions"] or []):
            for path in session["paths"]:
                if self.filter(session["endpoint"]):
                    self._render_path(path, "[snode]")

    @staticmethod
    def count_endpoints_in_path(paths, endpoint):
        num = 0
        for path in paths:
            if path['hops'][-1]['router'] == endpoint and path['ready']:
                num += 1
        return num

    @staticmethod
    def count_ready_paths(paths):
        num = 0
        for path in paths:
            if path['ready']:
                num += 1
        return num



    def display_data(self):
        """ draw main window """
        if self.data is not None:
            if self.version:
                print(1, 1, self.version)
            services = self.data["services"] or {}
            try:
                for key in services:
                    self.display_service(key, services[key])
            except Exception as ex:
                print('{}'.format(ex))
        else:
            self.win.move(1, 1)
            print("lokinet offline")

    def run(self):
        """ run mainloop """
        try:
            self.version = json.loads(self.rpc("llarp.version"))['result']['version']
        except:
            self.version = None

        while True:
            if self.update_data():
                self.display_data()
            elif True:
                print(1, 1, "offline")
            else:
                self._close()
                return
            try:
                time.sleep(1)
            except:
                self._close()
                return

def main():
    """ main function """

    ap = AP()

    ap.add_argument("--introset", action='store_const', const=True, default=False, help="run in introset inspection mode")
    ap.add_argument("--url", default='tcp://127.0.0.1:1190', type=str, help='url to lokinet rpc')
    ap.add_argument('--filter', default='.+', type=str, help="regex to filter entries")
    ap.add_argument('--invert-filter', const=True, default=False, action='store_const', help='invert regex filter matching')

    args = ap.parse_args()

    mon = Monitor(
        args.url
        )
    mon.filter = lambda x : re.match(args.filter, x) is not None
    if args.invert_filter:
        old_filter = mon.filter
        mon.filter = lambda x : not old_filter(x)
    mon.run()

if __name__ == "__main__":
    print("This script does not seem to work as intended!")
    quit(0)
    main()
