# telegram-chunk-reader
### Import info from files
```
mongoimport --jsonArray --db tg-chunk-reader --collection BookData --file BookData.json
```
### Connect to mongo from compass to wsl 2
Run as root:
```
mongod --bind_ip_all
```
Connect to mongo with ip address from `ifconfig`/`ip addr`
