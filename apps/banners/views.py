import json

from django.conf import settings
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import get_language

from badges.utils import handle_affiliate_link
from badges.views import dashboard
from banners.urls import AFFILIATE_LINK
from banners.models import Banner, BannerImage, BannerInstance, BANNER_TEMPLATE


def customize(request, banner_pk=None):
    banner = get_object_or_404(Banner, pk=banner_pk)
    banner_images = banner.bannerimage_set.filter(locale=get_language())

    # In case of no matches, default to the installation language
    if not banner_images:
        banner_images = (banner.bannerimage_set.
                         filter(locale=settings.LANGUAGE_CODE.lower()))

    json_banner_images = json.dumps(banner_images.size_color_to_image_map())
    json_size_colors = json.dumps(banner_images.size_to_color_map())
    affiliate_link = AFFILIATE_LINK % (request.user.pk, banner.pk)

    return dashboard(request, 'banners/customize.html',
                        {'banner': banner,
                         'affiliate_link': affiliate_link,
                         'subcategory': banner.subcategory,
                         'template': BANNER_TEMPLATE,
                         'json_banner_images': json_banner_images,
                         'json_size_colors': json_size_colors})


# TODO: Remove need for banner_id in link
def link(request, user_id, banner_id, banner_img_id):
    try:
        instance, created = (BannerInstance.objects.select_related()
                             .get_or_create(user_id=user_id,
                                            badge_id=banner_id,
                                            image_id=banner_img_id))
    except (IntegrityError):
        return HttpResponseRedirect(settings.DEFAULT_AFFILIATE_LINK)

    if created:
        banner_img = BannerImage.objects.select_related().get(pk=banner_img_id)
        instance.badge = banner_img.banner
        instance.save()

    return handle_affiliate_link(instance)
