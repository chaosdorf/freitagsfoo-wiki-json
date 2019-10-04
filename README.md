# freitagsfoo-wiki-json

(See the master branch for the normal version.)

creates a current `lightning-talks.json` from the current wiki entry

It is intended to be deployed to a server (currently `shells.chaosdorf.de`) invoked regularly via cron or systemd. The resulting JSON file is then pushed to an accessible path (currently `https://www.chaosdorf.de/~ytvwld/lightning-talks.json`).
