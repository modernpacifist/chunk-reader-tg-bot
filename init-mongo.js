db.createUser({
    user: 'log',
    pwd: 'pass',
    roles: [
        {
            role: 'readWrite',
            db: 'tg-chunk-reader',
        },
    ],
});

db = new Mongo().getDB("tg-chunk-reader");
