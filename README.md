# samp-query

Ask any SA-MP / open.mp server who it is, from the command line. A dependency-free implementation of the classic SA-MP UDP query protocol (info, rules, player list, detailed players, ping), usable as a CLI or imported as a tiny library.

## Usage

```bash
python3 samp_query.py 3.106.131.29:7777
python3 samp_query.py play.example.com:7777 --players --rules
python3 samp_query.py host:port --json
```

Live output, queried from a real running server:

```
AMERTA ROLEPLAY INDONESIA - AMR v1.0.21 Arunika -
gamemode : AMR v1.0.21 Arunika  (English)
players  : 0/496   ping 5.1 ms

rules:
  lagcomp          On
  mapname          San Andreas
  version          0.3.7-R2
```

## As a library

```python
from samp_query import SampServer
srv = SampServer("3.106.131.29", 7777)
print(srv.info())     # hostname, gamemode, language, players, max_players, password
print(srv.players(detailed=True))
print(srv.rules())
print(srv.ping())
```

Useful for server status pages, Discord bot presence, monitoring scripts, and launchers. No third-party packages, just sockets and struct.

## Indonesian summary

Alat query server SA-MP / open.mp lewat protokol UDP klasik: info server, rules, daftar pemain, dan ping. Tanpa dependensi, bisa jadi CLI atau pustaka untuk halaman status dan bot Discord.

## License

MIT. By ptraaa (AMERTA Roleplay).

## Support

If this project helped you, you can support its development on Trakteer: https://trakteer.id/adel_putra2

Kalau proyek ini membantu Anda, Anda bisa mendukung pengembangannya lewat Trakteer: https://trakteer.id/adel_putra2
