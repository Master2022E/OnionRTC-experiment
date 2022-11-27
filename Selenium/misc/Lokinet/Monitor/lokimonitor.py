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

    def __init__(self, url, introsetMode=False):
        self.txrate = 0
        self.rxrate = 0
        self.data = dict()
        self.win = curses.initscr()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        self._rpc_context = zmq.Context()
        self._rpc_socket = self._rpc_context.socket(zmq.DEALER)
        self._rpc_socket.setsockopt(zmq.CONNECT_TIMEOUT, 5000)
        self._rpc_socket.setsockopt(zmq.HANDSHAKE_IVL, 5000)
        self._rpc_socket.connect(url)
        self._speed_samples = [(0,0,0,0)] * self._sample_size
        self._run = True
        self._introsetMode = introsetMode

    def rpc(self, method):
        self._rpc_socket.send_multipart([method.encode(), b'lokinetmon'+method.encode()])
        if not self._rpc_socket.poll(timeout=50):
            return
        reply = self._rpc_socket.recv_multipart()
        if len(reply) >= 3 and reply[0:2] == [b'REPLY', b'lokinetmon'+method.encode()]:
            return reply[2].decode()

    def _close(self):
        self._rpc_socket.close(linger=0)
        self._run = False
        curses.endwin()

    def update_data(self):
        """update data from lokinet"""
        try:
            data = json.loads(self.rpc("llarp.status"))
            self.data = data['result']
        except:
            self.data = None
        return self.data is not None and self._run

    def _render_path(self, y_pos, path, name):
        """render a path at current position"""
        self.win.move(y_pos, 1)
        self.win.addstr("({}) ".format(name))
        y_pos += 1
        self.win.move(y_pos, 1)
        y_pos += 1
        self.win.addstr("[tx:\t{}]\t[rx:\t{}]".format(
            self.speed_of(path['txRateCurrent']), self.speed_of(path['rxRateCurrent'])))
        self.win.move(y_pos, 1)
        y_pos += 1
        self.win.addstr("me -> ")
        for hop in path["hops"]:
            hopstr = hop['router'][:4]
            if 'ip' in hop:
                hopstr += ' {}'.format(ip_to_flag(hop['ip']))
            self.win.addstr(" {} ->".format(hopstr))

        self.win.addstr(" [{} ms latency]".format(path["intro"]["latency"]))
        self.win.addstr(" [expires: {}]".format(self.time_to(path["expiresAt"])))
        if path["expiresSoon"]:
            self.win.addstr("(expiring)")
        elif path["expired"]:
            self.win.addstr("(expired)")
        return y_pos

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

    def display_service(self, y_pos, name, status):
        """display a service at current position"""
        self.win.move(y_pos, 1)
        self.win.addstr("service [{}]".format(name))
        build = status["buildStats"]
        ratio = build["success"] / (build["attempts"] or 1)
        y_pos += 1
        self.win.move(y_pos, 1)
        self.win.addstr("build success: {} %".format(int(100 * ratio)))
        y_pos += 1
        self.win.move(y_pos, 1)
        paths = status["paths"]
        self.win.addstr("paths: {}".format(len(paths)))
        for path in paths:
            if self.filter('localhost.loki'):
                y_pos = self._render_path(y_pos, path, "localhost.loki")
        for session in (status["remoteSessions"] or []):
            for path in session["paths"]:
                if self.filter(session["remoteIdentity"]):
                    y_pos = self._render_path(
                        y_pos, path, "[active] {}".format(session["currentConvoTag"])
                    )
        for session in (status["snodeSessions"] or []):
            for path in session["paths"]:
                if self.filter(session["endpoint"]):
                    y_pos = self._render_path(y_pos, path, "[snode]")
        return y_pos

    def display_links(self, y_pos, data):
        """ display links section """
        self.txrate = 0
        self.rxrate = 0
        for link in data["outbound"]:
            y_pos += 1
            self.win.move(y_pos, 1)
            self.win.addstr("outbound sessions:")
            y_pos = self.display_link(y_pos, link)
        for link in data["inbound"]:
            y_pos += 1
            self.win.move(y_pos, 1)
            self.win.addstr("inbound sessions:")
            y_pos = self.display_link(y_pos, link)
        y_pos += 2
        self.win.move(y_pos, 1)
        self.win.addstr(
            "throughput:\t\t[{}\ttx]\t[{}\trx]".format(
                self.speed_of(self.txrate), self.speed_of(self.rxrate)
            )
        )
        bloat_tx, bloat_rx = self.calculate_bloat(self.data['links']['outbound'])
        y_pos += 1
        self.win.move(y_pos, 1)
        self.win.addstr("goodput:\t\t[{}\ttx]\t[{}\trx]".format(
            self.speed_of(self.txrate-bloat_tx), self.speed_of(self.rxrate-bloat_rx)))
        y_pos += 1
        self.win.move(y_pos, 1)
        self.win.addstr("overhead:\t\t[{}\ttx]\t[{}\trx]".format(
            self.speed_of(bloat_tx), self.speed_of(bloat_rx)))
        self._speed_samples.append((self.txrate, self.rxrate, bloat_tx, bloat_rx))
        while len(self._speed_samples) > self._sample_size:
            self._speed_samples.pop(0)
        return self.display_speedgraph(y_pos + 2)

    @staticmethod
    def _scale(_x, _n):
        while _n > 0:
            _x /= 2
            _n -= 1
        return int(_x)


    @staticmethod
    def _makebar(samp, badsamp, maxsamp):
        barstr = "#" * (samp - badsamp)
        pad = " " * (maxsamp - samp)
        return pad, barstr, '#' * badsamp

    def display_speedgraph(self, y_pos, maxsz=40):
        """ display global speed graph """
        txmax, rxmax = 1024, 1024
        for _tx, _rx, b_tx, b_rx in self._speed_samples:
            if _tx > txmax:
                txmax = _tx
            if _rx > rxmax:
                rxmax = _rx

        rxscale = 0
        while rxmax > maxsz:
            rxscale += 1
            rxmax /= 2

        txscale = 0
        while txmax > maxsz:
            txscale += 1
            txmax /= 2

        txlabelpad = int(txmax / 2)
        rxlabelpad = int(rxmax / 2)
        if txlabelpad <= 0:
            txlabelpad = 1
        if rxlabelpad <= 0:
            rxlabelpad = 1
        txlabelpad_str = " " * txlabelpad
        rxlabelpad_str = " " * rxlabelpad
        y_pos += 1
        self.win.move(y_pos, 1)
        for val in [txlabelpad_str, 'tx', txlabelpad_str, rxlabelpad_str, 'rx', rxlabelpad_str]:
            self.win.addstr(val)
        for _tx, _rx, b_tx, b_rx in self._speed_samples:
            y_pos += 1
            self.win.move(y_pos, 1)
            txpad, txbar, btxbar = self._makebar(self._scale(_tx, txscale), self._scale(b_tx, txscale), int(txmax))
            rxpad, rxbar, brxbar = self._makebar(self._scale(_rx, rxscale), self._scale(b_rx, rxscale), int(rxmax))
            self.win.addstr(txpad)
            self.win.addstr(btxbar, curses.color_pair(1))
            self.win.addstr(txbar)
            self.win.addstr('|')
            self.win.addstr(rxbar)
            self.win.addstr(brxbar, curses.color_pair(1))
            self.win.addstr(rxpad)
        return y_pos + 2

    def calculate_bloat(self, links):
        """
        calculate bandwith overhead
        """
        paths = self.get_all_paths()
        lltx = 0
        llrx = 0
        _tx = 0
        _rx = 0
        for link in links:
            sessions = link["sessions"]["established"]
            for sess in sessions:
                lltx += sess['tx']
                llrx += sess['rx']
        for path in paths:
            _tx += path['txRateCurrent']
            _rx += path['rxRateCurrent']
        lltx -= _tx
        llrx -= _rx
        if lltx < 0:
            lltx = 0
        if llrx < 0:
            llrx = 0
        return lltx, llrx

    def display_link(self, y_pos, link):
        """ display links """
        y_pos += 1
        self.win.move(y_pos, 1)
        sessions = link["sessions"]["established"] or []
        for sess in sessions:
            y_pos = self.display_link_session(y_pos, sess)
        return y_pos

    def display_link_session(self, y_pos, sess):
        """ display link sessions """
        y_pos += 1
        self.win.move(y_pos, 1)
        self.txrate += sess["txRateCurrent"]
        self.rxrate += sess["rxRateCurrent"]
        addr = sess['remoteAddr']
        if geo:
            ip = addr.split(':')[0]
            addr += '\t{}'.format(ip_to_flag(ip))
        self.win.addstr(
            "{}\t[{}\ttx]\t[{}\trx]".format(
                addr, self.speed_of(sess["txRateCurrent"]), self.speed_of(sess["rxRateCurrent"])
            )
        )
        if (sess['txMsgQueueSize'] or 0) > 1:
            self.win.addstr(" [out window: {}]".format(sess['txMsgQueueSize']))
            if (sess['rxMsgQueueSize'] or 0) > 1:
                self.win.addstr(" [in window: {}]".format(sess['rxMsgQueueSize']))
        def display(acks, label, num='acks', dem='packets'):
            if acks[dem] > 0:
                self.win.addstr(" [{}: {}]".format(label, round(float(acks[num]) / float(acks[dem]), 2)))
        if ('recvMACKs' in sess) and ('sendMACKs' in sess):
            display(sess['sendMACKs'], 'out MACK density')
            display(sess['recvMACKs'], 'in MACK density')
        dats = {'recvAcks': 'in acks',
                'sendAcks': 'out acks',
                'recvRTX': 'in RTX',
                'sendRTX': 'out RTX'}
        for key in dats:
            val = dats[key]
            if (key in sess) and (sess[key] > 0):
                self.win.addstr(" [{}: {}]".format(val, sess[key]))
        return y_pos

    def display_dht(self, y_pos, data):
        """ display dht window """
        y_pos += 2
        self.win.move(y_pos, 1)
        self.win.addstr("DHT:")
        y_pos += 1
        self.win.move(y_pos, 1)
        self.win.addstr("introset lookups")
        y_pos = self.display_bucket(y_pos, data["pendingIntrosetLookups"])
        y_pos += 1
        self.win.move(y_pos, 1)
        self.win.addstr("router lookups")
        return self.display_bucket(y_pos, data["pendingRouterLookups"])

    def display_bucket(self, y_pos, data):
        """ display dht bucket """
        txs = data["tx"]
        self.win.addstr(" ({} lookups)".format(len(txs)))
        for transaction in txs:
            y_pos += 1
            self.win.move(y_pos, 1)
            self.win.addstr("search for {}".format(transaction["tx"]["target"]))
        return y_pos



    def display_introsets(self, y_pos, service):
        """
        display introsets on a service
        """
        y_pos += 1
        self.win.move(y_pos, 1)
        if self.filter("localhost.loki"):
            self.win.addstr("localhost.loki")
            y_pos = self._display_our_introset(y_pos, service)
            y_pos += 1
        remotes = service['remoteSessions'] or []
        for session in remotes:
            if self.filter(session['remoteIdentity']):
                y_pos = self._display_session_introset(y_pos, session)

    def _display_intro(self, y_pos, intro, label, paths):
        y_pos += 1
        self.win.move(y_pos, 1)
        path = 'path' in intro and intro['path'][:4] or '????'
        self.win.addstr('{}: ({}|{}) [expires: {}] [{} paths]'.format(label, intro['router'][:8], path, self.time_to(intro['expiresAt']), self.count_endpoints_in_path(paths, intro['router'])))
        return y_pos

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



    @staticmethod
    def make_bar(timestamp, scale=1, char='#'):
        if timestamp > 0:
            return int((abs(timestamp - now()) / 1000) / scale) * char
        return ''

    def _display_our_introset(self, y_pos, context):
        for intro in context['introset']['intros'] or []:
            y_pos = self._display_intro(y_pos, intro, "introset intro", context['paths'])
        for path in context['paths']:
            y_pos = self._display_intro(y_pos, path['intro'], "inbound path [created {}]".format(self.time_to(path['buildStarted'])), context['paths'])
        return y_pos


    def _display_session_introset(self, y_pos, context):
        #print(context.keys())
        y_pos += 1
        self.win.move(y_pos, 1)
        readyState = context['readyToSend'] and '??' or '?'
        self.win.addstr('{} ({}) [{}]'.format(context['remoteIdentity'], context['currentConvoTag'], readyState))
        y_pos += 1
        self.win.move(y_pos, 1)
        self.win.addstr('created: {}'.format(self.time_to(context['sessionCreatedAt'])))
        y_pos += 1
        self.win.move(y_pos, 1)
        self.win.addstr('last good send: {}'.format(self.time_to(context['lastGoodSend'])))
        y_pos += 1
        self.win.move(y_pos, 1)
        self.win.addstr(self.make_bar(context['lastGoodSend']))
        y_pos += 1
        self.win.move(y_pos, 1)
        self.win.addstr('last recv: {}'.format(self.time_to(context['lastRecv'])))
        y_pos += 1
        self.win.move(y_pos, 1)
        self.win.addstr(self.make_bar(context['lastRecv']))
        y_pos += 1
        self.win.move(y_pos, 1)
        self.win.addstr('last introset update: {}'.format(self.time_to(context['lastIntrosetUpdate'])))
        y_pos += 1
        self.win.move(y_pos, 1)
        self.win.addstr(self.make_bar(context['lastIntrosetUpdate'], 30))
        y_pos += 2

        self.win.move(y_pos, 1)
        self.win.addstr('last shift: {}'.format(self.time_to(context['lastShift'])))

        paths = context['paths'] or []

        y_pos = self._display_intro(y_pos + 1, context['nextIntro'], 'next intro', paths) + 1
        y_pos = self._display_intro(y_pos, context['remoteIntro'], 'current intro', paths) + 1
        for intro in context['currentRemoteIntroset']['intros'] or []:
            y_pos = self._display_intro(y_pos, intro, "introset intro", paths)
        y_pos += 1
        return y_pos

    def display_data(self):
        """ draw main window """
        if self.data is not None:
            if self.version:
                self.win.addstr(1, 1, self.version)
            services = self.data["services"] or {}
            y_pos = 3
            try:
                if not self._introsetMode:
                    y_pos = self.display_links(y_pos, self.data["links"])
                    for key in services:
                        y_pos = self.display_service(y_pos, key, services[key])
                    y_pos = self.display_dht(y_pos, self.data["dht"])
                else:
                    for key in services:
                        y_pos = self.display_introsets(y_pos, services[key])
            except Exception as ex:
                print('{}'.format(ex))
        else:
            self.win.move(1, 1)
            self.win.addstr("lokinet offline")

    def run(self):
        """ run mainloop """
        try:
            self.version = json.loads(self.rpc("llarp.version"))['result']['version']
        except:
            self.version = None

        while self._run:
            if self.update_data():
                self.win.box()
                self.display_data()
            elif self._run:
                self.win.addstr(1, 1, "offline")
            else:
                self._close()
                return
            self.win.refresh()
            try:
                time.sleep(1)
            except:
                self._close()
                return
            self.win.clear()

def main():
    """ main function """

    ap = AP()

    ap.add_argument("--introset", action='store_const', const=True, default=False, help="run in introset inspection mode")
    ap.add_argument("--url", default='tcp://127.0.0.1:1190', type=str, help='url to lokinet rpc')
    ap.add_argument('--filter', default='.+', type=str, help="regex to filter entries")
    ap.add_argument('--invert-filter', const=True, default=False, action='store_const', help='invert regex filter matching')

    args = ap.parse_args()

    mon = Monitor(
        args.url,
        args.introset
    )
    mon.filter = lambda x : re.match(args.filter, x) is not None
    if args.invert_filter:
        old_filter = mon.filter
        mon.filter = lambda x : not old_filter(x)
    mon.run()

if __name__ == "__main__":
    main()
