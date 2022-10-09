import datetime

now = datetime.datetime.now()


def year(request):
    return {
        'year': now.year,
    }
