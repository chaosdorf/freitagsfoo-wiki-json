# freitagsfoo-wiki-json
creates a current `freitagsfoo.json` from the current wiki entry

It is intended to be deployed to a server (currently `shells.chaosdorf.de`) invoked regularly via cron or systemd. The resulting JSON file is then pushed to an accessible path (currently `https://www.chaosdorf.de/~ytvwld/freitagsfoo.json`).
