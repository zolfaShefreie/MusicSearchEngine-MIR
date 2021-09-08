

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
                        "filter": ["synonym1", "synonym2", "synonym3", "synonym4", "synonym5", "synonym6",
                                   "synonym7", "synonym8", "synonym9", "synonym10", "synonym11", "synonym12",
                                   "synonym13", "synonym14", "synonym15", "synonym16"]
                    }
                },
                "filter": {
                    "synonym1": {
                        "type": "synonym",
                        "lenient": True,
                        "synonyms_path": "./fingerprint_24bit/synonyms1.txt"
                    },
                    "synonym2": {
                        "type": "synonym",
                        "lenient": True,
                        "synonyms_path": "./fingerprint_24bit/synonyms2.txt"
                    },
                    "synonym3": {
                        "type": "synonym",
                        "lenient": True,
                        "synonyms_path": "./fingerprint_24bit/synonyms3.txt"
                    },
                    "synonym4": {
                        "type": "synonym",
                        "lenient": True,
                        "synonyms_path": "./fingerprint_24bit/synonyms4.txt"
                    },
                    "synonym5": {
                        "type": "synonym",
                        "lenient": True,
                        "synonyms_path": "./fingerprint_24bit/synonyms5.txt"
                    },
                    "synonym6": {
                        "type": "synonym",
                        "lenient": True,
                        "synonyms_path": "./fingerprint_24bit/synonyms6.txt"
                    },
                    "synonym7": {
                        "type": "synonym",
                        "lenient": True,
                        "synonyms_path": "./fingerprint_24bit/synonyms7.txt"
                    },
                    "synonym8": {
                        "type": "synonym",
                        "lenient": True,
                        "synonyms_path": "./fingerprint_24bit/synonyms8.txt"
                    },
                    "synonym9": {
                        "type": "synonym",
                        "lenient": True,
                        "synonyms_path": "./fingerprint_24bit/synonyms9.txt"
                    },
                    "synonym10": {
                        "type": "synonym",
                        "lenient": True,
                        "synonyms_path": "./fingerprint_24bit/synonyms10.txt"
                    },
                    "synonym11": {
                        "type": "synonym",
                        "lenient": True,
                        "synonyms_path": "./fingerprint_24bit/synonyms11.txt"
                    },
                    "synonym12": {
                        "type": "synonym",
                        "lenient": True,
                        "synonyms_path": "./fingerprint_24bit/synonyms12.txt"
                    },
                    "synonym13": {
                        "type": "synonym",
                        "lenient": True,
                        "synonyms_path": "./fingerprint_24bit/synonyms13.txt"
                    },
                    "synonym14": {
                        "type": "synonym",
                        "lenient": True,
                        "synonyms_path": "./fingerprint_24bit/synonyms14.txt"
                    },
                    "synonym15": {
                        "type": "synonym",
                        "lenient": True,
                        "synonyms_path": "./fingerprint_24bit/synonyms15.txt"
                    },
                    "synonym16": {
                        "type": "synonym",
                        "lenient": True,
                        "synonyms_path": "./fingerprint_24bit/synonyms16.txt"
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
