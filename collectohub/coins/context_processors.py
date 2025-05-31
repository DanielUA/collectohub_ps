from .models import *


def statistics_processor(request):
    path = request.path.rstrip("/") or "/"
    seo = PageSeo.objects.filter(url=path).first()
    return {
        'num_coins': Coin.objects.filter(status='a').count(),
        "title": seo.title if seo else "",
        "description": seo.description if seo else "",
        'global_scripts_head': GlobalScript.objects.filter(position='head', is_active=True),
        'global_scripts_body_top': GlobalScript.objects.filter(position='body_top', is_active=True),
        'global_scripts_body_bottom': GlobalScript.objects.filter(position='body_bottom', is_active=True),
    }