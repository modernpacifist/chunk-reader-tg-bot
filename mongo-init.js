use admin;

db.createUser({
    user: 'log',
    pwd: 'pass',
    roles: [
        {
            role: 'readWrite', db: 'tg-chunk-reader',
        },
    ],
});
