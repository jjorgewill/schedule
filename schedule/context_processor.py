from apps.core.models import Feature


def menu(request):
    if request.user.is_authenticated():
        permitions = request.user.user_permissions.all()
        features = Feature.objects.filter(permition__in=permitions).order_by('position')
        context_default={"features":features}
    else:
        context_default = {}
    return context_default