from django.urls import path
from .views import predict_disease
from .views import job_vibe

urlpatterns = [
    path("predict/", predict_disease, name="predict_disease"),
    path("jobvibe/", job_vibe, name="job_vibe"),
]
