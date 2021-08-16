from django.core.management.base import BaseCommand
from django.conf import settings
import requests

MUSICBRAINZ_CONF = getattr(settings, 'MUSIC_BRAINS', {})


class Command(BaseCommand):
    TEMPORARY_DER = "./mir_sys/artist_folder"
    
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.file_path = str()

    def handle(self, *args, **kwargs):
        pass

    def download_file(self):
        """"
        download music brain artist file from url
        """
        url = MUSICBRAINZ_CONF['JSON_FILE_URL']
        file_name = url.split('/')[-1]
        r = requests.get(url, allow_redirects=True)
        self.file_path = f"{self.TEMPORARY_DER}/{file_name}"
        open(self.file_path, 'wb').write(r.content)

    def extract_file(self):
        pass
