from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_video, name='upload_video'),
    # path('filter_videos/', views.filter_videos, name='filter_videos'),
    path('all_view_video_api/', views.all_view_video_api, name='all_view_video_api'),    
    path("filter_videos", views.filter_videos.as_view(), name="filter_videos"),
    
]
