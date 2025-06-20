from django.conf import settings
from django.http import HttpResponseRedirect
from core.models import MaintenanceMode

class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        maintenance_status = MaintenanceMode.objects.first()
        if maintenance_status:
            if maintenance_status.on == True:
                current_path = request.path
                if (
                    current_path.startswith('/admin/')
                    or current_path.startswith('/admin_dashboard/')
                    or current_path == settings.MAINTENANCE_REDIRECT_URL
                ):
                    return self.get_response(request)

                if request.user.is_authenticated and request.user.is_staff:
                    return self.get_response(request)
                return HttpResponseRedirect(settings.MAINTENANCE_REDIRECT_URL)    
        return self.get_response(request)
