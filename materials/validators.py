from django.core.exceptions import ValidationError

class YoutubeValidators:

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        video_url = value.get(self.field)
        if video_url and not video_url.startswith('https://www.youtube.com/'):
            raise ValidationError('Неразрешенная ссылка')