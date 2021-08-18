from django.core.management.base import BaseCommand
from django.conf import settings
import requests
import tarfile
import json
import shutil

from mir_sys.utils.util_classes import CDict


MUSICBRAINZ_CONF = getattr(settings, 'MUSIC_BRAINS', {})


class Command(BaseCommand):
    TEMPORARY_DIR = "./mir_sys/artist_folder"
    
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.file_path = str()

    def handle(self, *args, **kwargs):
        self.download_file()
        self.extract_file()
        num, artists = self.get_artist_tokens()
        print(f"number of artists: {num}")
        self.delete_the_folder()
        self.save_tokens(artists)
        print("file saved")

    def download_file(self):
        """"
        download music brain artist file from url
        """
        url = MUSICBRAINZ_CONF['JSON_FILE_URL']
        file_name = url.split('/')[-1]
        r = requests.get(url, allow_redirects=True)
        self.file_path = f"{self.TEMPORARY_DIR}/{file_name}"
        open(self.file_path, 'wb').write(r.content)

    def extract_file(self):
        """
        extract tar file
        """
        try:
            tf = tarfile.open(self.file_path)
            tf.extractall(self.TEMPORARY_DIR)
        except Exception as e:
            print("Error:", str(e))

    def get_artist_tokens(self) -> (int, set):
        """
        get all tokens of artist for searching in youtube music
        one artist object save as json in every line of file

        :returns number of artists , artist tokens
        """
        main_file_path = f"{self.TEMPORARY_DIR}{MUSICBRAINZ_CONF['ARTIST_FILE_PATH']}"
        artists = str()
        file = open(main_file_path, encoding="utf8")
        artists_num = 1
        for line in file:
            if line != "\n":
                try:
                    artist_obj = json.loads(line)
                    artists += f" {artist_obj.get('name', '')}"
                    artists_num += 1
                except:
                    pass
        file.close()
        return artists_num, set(artists.lower().split(" "))

    def delete_the_folder(self):
        try:
            shutil.rmtree(self.TEMPORARY_DIR)
        except Exception as e:
            print(e)

    def save_tokens(self, artists):
        """
        save token files
        :param artists: list of tokens
        """
        tokens = CDict(MUSICBRAINZ_CONF['ARTIS_TOKEN_PATH'])
        for each in artists:
            tokens.update({each: False})
        tokens.save()
