import validators


def validate_url(url):
    if not url:
        return 'URL обязателен', 'danger'
    elif not validators.url(url):
        return 'Некорректный URL', 'danger'
