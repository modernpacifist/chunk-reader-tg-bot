# telegram-chunk-reader
### Read everything about this project
Paper on medium https://medium.com/@modernpacifist/telegram-chunk-reader-3640b89df2d8
### For dev
#### Import info from files
```
$ mongoimport --jsonArray --db tg-chunk-reader --collection BookData --file BookData.json
```
#### Connect to mongo from compass to wsl2
Run as root in wsl2 shell:
```
# mongod --bind_ip_all
```
Connect to mongo with ip address from `ifconfig`/`ip addr`
