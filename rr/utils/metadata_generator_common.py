from rr.models.serviceprovider import ServiceProvider


def get_entity(sp, validated):
    """Set history object if using validated metadata and newest version is not validated.
    Set validation_date to last point where metadata was validated"""
    if validated and not sp.validated:
        history = ServiceProvider.objects.filter(history=sp.pk).exclude(validated=None).last()
        if not history:
            return None, None, None
        validation_date = history.validated
    else:
        history = None
        if validated:
            validation_date = sp.validated
        else:
            validation_date = None

    if history:
        entity = history
    else:
        entity = sp

    return entity, history, validation_date
