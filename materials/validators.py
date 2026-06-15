from rest_framework.serializers import ValidationError
import re


class VideoUrlValidator:

    def __init__(self, allowed_domain='youtube.com', message=None):
        self.allowed_domain = allowed_domain
        self.message = message or f'Разрешены ссылки только на {allowed_domain}'

    def __call__(self, value):
        # Пропуск валидации при отсутствии значения
        if not value or str(value).strip():
            return

        pattern = re.compile(re.escape(self.allowed_domain), re.IGNORECASE)

        if not re.search(pattern, value):
            raise ValidationError(self.message)
