#!/usr/bin/env python3
"""
samp-query - ask any SA-MP / open.mp server who it is, from the command line.

Implements the classic SA-MP UDP query protocol (opcodes i, r, c, d, p):
server info, rules, player list, detailed player list, and ping. Standard
library only. Use it as a CLI or import it as a tiny library.

    python3 samp_query.py 3.106.131.29:7777
    python3 samp_query.py play.example.com:7777 --players --rules
    python3 samp_query.py host:port --json

By ptraaa - MIT License
"""
import argparse, json, socket, struct, sys


class SampServer:
    def __init__(self, host, port=7777, timeout=3.0):
        if ":" in str(host):
            host, port = host.rsplit(":", 1)
            port = int(port)
        self.host = socket.gethostbyname(host)
        self.port = int(port)
        self.timeout = timeout

    def _ask(self, opcode, payload=b""):
        ip = b"".join(bytes([int(x)]) for x in self.host.split("."))
        packet = b"SAMP" + ip + struct.pack("<H", self.port) + opcode + payload
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(self.timeout)
            s.sendto(packet, (self.host, self.port))
            data, _ = s.recvfrom(4096)
        if data[:4] != b"SAMP" or data[10:11] != opcode:
            raise ValueError("unexpected reply from server")
        return data[11:]

    @staticmethod
    def _str(buf, off):
        ln = struct.unpack_from("<I", buf, off)[0]
        off += 4
        return buf[off:off + ln].decode("utf-8", errors="replace"), off + ln

    @staticmethod
    def _short_str(buf, off):
        ln = buf[off]
        off += 1
        return buf[off:off + ln].decode("utf-8", errors="replace"), off + ln

    def info(self):
        b = self._ask(b"i")
        password = bool(b[0])
        players, maxplayers = struct.unpack_from("<HH", b, 1)
        hostname, off = self._str(b, 5)
        gamemode, off = self._str(b, off)
        language, off = self._str(b, off)
        return {"hostname": hostname, "gamemode": gamemode, "language": language,
                "players": players, "max_players": maxplayers, "password": password}

    def rules(self):
        b = self._ask(b"r")
        count = struct.unpack_from("<H", b, 0)[0]
        off, out = 2, {}
        for _ in range(count):
            k, off = self._short_str(b, off)
            v, off = self._short_str(b, off)
            out[k] = v
        return out

    def players(self, detailed=False):
        b = self._ask(b"d" if detailed else b"c")
        count = struct.unpack_from("<H", b, 0)[0]
        off, out = 2, []
        for _ in range(count):
            pid = b[off]
            off += 1
            name, off = self._short_str(b, off)
            score = struct.unpack_from("<i", b, off)[0]
            off += 4
            entry = {"id": pid, "name": name, "score": score}
            if detailed:
                entry["ping"] = struct.unpack_from("<I", b, off)[0]
                off += 4
            out.append(entry)
        return out

    def ping(self):
        import time
        payload = struct.pack("<I", 1234567890)
        start = time.time()
        b = self._ask(b"p", payload)
        ms = (time.time() - start) * 1000
        if struct.unpack("<I", b[:4])[0] != 1234567890:
            raise ValueError("bad ping reply")
        return round(ms, 1)


def main():
    ap = argparse.ArgumentParser(description="Query a SA-MP / open.mp server")
    ap.add_argument("server", help="host or host:port (default port 7777)")
    ap.add_argument("--players", action="store_true", help="list players (detailed)")
    ap.add_argument("--rules", action="store_true", help="show server rules")
    ap.add_argument("--json", action="store_true", help="JSON output")
    ap.add_argument("--ptraaa", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args()
    if args.ptraaa:
        print('samp-query, by ptraaa of AMERTA Roleplay. Sampai jumpa di Los Santos. More small tools: github.com/Ptraaah')
        return

    srv = SampServer(args.server)
    try:
        result = srv.info()
        result["ping_ms"] = srv.ping()
        if args.rules:
            result["rules"] = srv.rules()
        if args.players:
            result["player_list"] = srv.players(detailed=True)
    except Exception as e:
        print(f"could not reach {args.server}: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return
    print(f"{result['hostname']}")
    print(f"gamemode : {result['gamemode']}  ({result['language']})")
    print(f"players  : {result['players']}/{result['max_players']}"
          f"{'  [passworded]' if result['password'] else ''}   ping {result['ping_ms']} ms")
    if "rules" in result:
        print("\nrules:")
        for k, v in result["rules"].items():
            print(f"  {k:16s} {v}")
    if "player_list" in result:
        print("\nplayers:")
        for p in result["player_list"]:
            print(f"  [{p['id']:3d}] {p['name']:24s} score {p['score']:6d}  ping {p['ping']} ms")


if __name__ == "__main__":
    main()
