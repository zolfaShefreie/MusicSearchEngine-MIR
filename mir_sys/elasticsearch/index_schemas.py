

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
                "songs": {"type": "keyword"}
            }
        }
    },
    "index_name": "fingerprints"
}

SONG_INDEX = {
    "schema": {
        "settings": {
            "analysis": {
                "analyzer": {
                    "fingerprint_analyzer": {
                        "tokenizer": "fingerprint_tokenizer",
                        "filter": ["synonym" ]
                    }
                },
                "filter": {
                    "synonym": {
                        "type": "synonym",
                        "lenient": True,
                        "synonyms_path": "./fingerprint_24bit/synonym.txt"
                    }
                },
                "tokenizer": {
                    "fingerprint_tokenizer": {
                        "type": "simple_pattern",
                        "pattern": ".{4}"
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "artist": {"type": "keyword"},
                "effort": {"type": "integer"},
                "fingerprint": {
                    "type": "text",
                    "search_analyzer": "fingerprint_analyzer",
                    "analyzer": "fingerprint_analyzer"
                }
            }
        }
    },
    "index_name": "songs"
}

# this object get to create indexes
SCHEMA = [
    ARTIST_INDEX, SONG_INDEX, FINGERPRINT_INDEX
]
