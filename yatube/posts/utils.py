from django.conf import settings as s
from django.core.paginator import Paginator


def get_page_context(queryset, request):
    paginator = Paginator(queryset, s.NUM_REC)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'page_obj': page_obj,
    }
