# MusicSearchEngine-MIR
search by sound system and use [audioFingerprint model project](https://github.com/zolfaShefreie/AudioFingerprintModel)
## commands
use can access commands with python manage.py [command]
artist_tokens => create artist token by downloading musicbrainz database files</br>
insert_indices => insert indices to elasticsearch server. you should provide synonyms files from [here]()</br>
add_fingerprints => add all fingerprints for create hash table in elasticsearch</br>
delete_indices => delete all indices of this project from elasticsearch</br>
explore => start collocting data of search engine</br>
you can access the apis by runserver command
