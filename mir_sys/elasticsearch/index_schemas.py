

ARTIST_INDEX = {
    "schema": {
        "mappings": {
            "properties": {
                "last_check": {"type": "date"},
            }
        }
    },
    "index_name": "artists"
}

FINGERPRINT_INDEX = {
    "schema": {
        "mappings": {
            "properties": {
                "rel_fingerprint": {"type": "keyword", "store": True},
                "songs": {"type": "keyword", "store": True}
            }
        }
    },
    "index_name": "fingerprints"
}

SONG_INDEX = {
    "schema": {
        "mappings": {
            "properties": {
                "artist": {"type": "keyword", "store": True},
                "seen": {"type": "boolean"},
                "fingerprint": {"type": "wildcard"}
            }
        }
    },
    "index_name": "songs"
}

# this object get to create indexes
SCHEMA = [
    ARTIST_INDEX, SONG_INDEX, FINGERPRINT_INDEX
]
