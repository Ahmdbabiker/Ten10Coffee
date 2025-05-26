from .models import City


def cities(request):
    cities = City.objects.all()
    return {'cities':cities}
