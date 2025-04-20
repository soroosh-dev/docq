from rest_framework.exceptions import NotFound


def custom_get_or_404(model,*args, **kwargs):
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        raise NotFound(
            f"{model._meta.object_name} not found."
        )