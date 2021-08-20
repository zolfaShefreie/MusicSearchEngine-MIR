import youtube_dl
import time
from django.conf import settings


DOWNLOAD_PATH = getattr(settings, 'DOWNLOAD_PATH', 1)


class Downloader:
    MAX_DURATION = 600
    MAX_SIZE = 10485760  # 10M

    @staticmethod
    def download_music(music_urls: list):
        """
        download audios based on music_urls
        :param music_urls:
        :return:
        """

        ydl_opts = {

            'force-ipv4': True,
            "external-downloader": "aria2c",
            "external-downloader-args": "-x 16 -s 16 -k 1M",
            'ignoreerrors': True,
            'format': 'bestaudio/best',
            'extractaudio': True,      # only keep the audio
            'audioformat': "wav",      # convert to wav
            'outtmpl': f'{DOWNLOAD_PATH}%(id)s.wav',        # name the file the ID of the video
            'noplaylist': True,
            'max-filesize': '10m',
            'quiet': True,
            'no-warnings': True
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download(music_urls)

    @staticmethod
    def get_youtube_urls(music_ids: list) -> list:
        """
        convert id to youtube urls
        example:
        7ZUMRECYLOQ => https://www.youtube.com/watch?v=7ZUMRECYLOQ
        :param music_ids:
        :return: a list of urls
        """
        base_url = "https://music.youtube.com/watch?v={}"
        return [base_url.format(music_id) for music_id in music_ids]

    @classmethod
    def check_download_permissions(cls, music_urls: list) -> list:
        """
        if the size or duration is ok it is allowed to download
        :param music_urls:
        :return: a list of url that has permission to download
        """

        allowed = list()
        for url in music_urls:
            audio_downloader = youtube_dl.YoutubeDL({'format': 'bestaudio',
                                                     "external-downloader": "aria2c",
                                                     "external-downloader-args": "-x 16 -s 16 -k 1M",
                                                     'ignoreerrors': True,
                                                     'quiet': True,
                                                     'no-warnings': True})
            info = audio_downloader.extract_info(url, download=False)
            if info and info.get('duration', float('inf')) <= cls.MAX_DURATION and \
                    info.get('filesize', float('inf')) <= cls.MAX_SIZE:
                allowed.append(url)
            if not info:
                time.sleep(0.2)
        return allowed

    @classmethod
    def download_manager(cls, ids: list):
        """
        :param ids: list of music ids
        :return:
        """
        allowed_music = cls.check_download_permissions(cls.get_youtube_urls(ids))
        cls.download_music(allowed_music)
