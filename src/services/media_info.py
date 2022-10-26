from schemas import MediaInfoSchema
import ffmpeg
import json
import hashlib


class MediaInfoServices:

    def __init__(self, file_path):
        self.probe = ffmpeg.probe(file_path)

    @property
    def video(self):
        return next((stream for stream in self.probe['streams'] if stream['codec_type'] == 'video'), None)

    @property
    def audio(self):
        return next((stream for stream in self.probe['streams'] if stream['codec_type'] == 'audio'), None)

    @property
    def format(self):
        return self.probe.get('format', None)

    @property
    def size(self):
        w = self.video.get('width')
        h = self.video.get('height')
        return f"{w}x{h}"

    @property
    def short_info(self):
        return MediaInfoSchema(
            size=self.size,
            vcodec=self.video.get('codec_name'),
            acodec=self.audio.get('codec_name'),
            duration=self.format.get('duration'),
            format=self.format.get('format_name'),
        )

    @property
    def hash_params(self):
        params = dict(
            size=self.size,
            vcodec=self.video.get('codec_name'),
            acodec=self.audio.get('codec_name'),
            format=self.format.get('format_name'),
        )
        b_json = json.dumps(params).encode('utf-8')
        return hashlib.sha256(b_json).hexdigest()
