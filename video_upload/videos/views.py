from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Video
import re
import datetime
from django.utils.dateparse import parse_datetime
from .serializers import VideoSerializer

from django.db.models import Q
from django.conf import settings


from rest_framework.views import APIView
from django.utils.dateparse import parse_datetime


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView



@csrf_exempt
def upload_video(request):
    if request.method == 'POST':
        file = request.FILES.get('video')
        if not file:
            return JsonResponse({"error": "No video file provided."}, status=400)

        filename = file.name

        pattern = r"^\d{8}\d{6}-\d{8}\d{6}\.mp4$"
        if not re.match(pattern, filename):
            return JsonResponse({"error": "Invalid file name format. Use DDMMYYYYHHMMSS-DDMMYYYYHHMMSS.mp4"}, status=400)

        try:
            start_time_str, end_time_str = filename.split('-')
            end_time_str = end_time_str.split('.')[0]
            start_timestamp = datetime.datetime.strptime(start_time_str, '%d%m%Y%H%M%S')
            end_timestamp = datetime.datetime.strptime(end_time_str, '%d%m%Y%H%M%S')
            if start_timestamp >= end_timestamp:
                return JsonResponse({"error": "Start timestamp must be earlier than end timestamp."}, status=400)
        except ValueError:
            return JsonResponse({"error": "Error parsing timestamps from filename."}, status=400)

        video_instance = Video.objects.create(
            name=filename,
            video_file=file,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp
        )

        return JsonResponse({
            "message": "Video uploaded successfully.",
            "video": {"name": video_instance.name, "url": video_instance.video_file.url}
        }, status=201)
    
@api_view(['GET'])
def all_view_video_api(request):
    user_videos = Video.objects.all()
    if user_videos.count() > 0:
        serializer = VideoSerializer(user_videos, many=True)
        return Response({'data': serializer.data, 'message': 'Data fetched successfully', 'success': True}, status=status.HTTP_200_OK)
    else:
        return Response({'data': 'No data available'}, status=status.HTTP_400_BAD_REQUEST)
    
    
# class VideoPagination(PageNumberPagination):
#     page_size = 10

# @api_view(['GET'])
# def all_view_user_api(request):
#     paginator = VideoPagination()
#     videos = Video.objects.all()
#     paginated_videos = paginator.paginate_queryset(videos, request)
#     serializer = VideoSerializer(paginated_videos, many=True)
#     return paginator.get_paginated_response(serializer.data)
    
    
# class filter_videos(GenericAPIView):
#     def post(self, request):
#         starting = request.data.get('starting')
#         ending = request.data.get('ending')

#         if (starting != "" and ending != ""):
#             queryset = Video.objects.filter(
#                 Q(start_timestamp__gte=starting) & Q(end_timestamp__lte=ending)).values()

#             return Response({'data': (queryset), 'message': 'Successfully fetched', 'success': True}, status=status.HTTP_200_OK)
#         else:
#             return Response({'message': 'no result found', 'success': True}, status=status.HTTP_200_OK)
        
        
class filter_videos(APIView):
    def post(self, request):
        starting = request.data.get('starting')
        ending = request.data.get('ending')

        # Validate input
        if not starting or not ending:
            return Response(
                {'message': 'Both starting and ending timestamps are required.', 'success': False},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Parse and validate the datetime strings
            starting = parse_datetime(starting)
            ending = parse_datetime(ending)

            if not starting or not ending:
                raise ValueError("Invalid datetime format.")

            if starting >= ending:
                return Response(
                    {'message': 'The starting timestamp must be earlier than the ending timestamp.', 'success': False},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError as e:
            return Response(
                {'message': f'Error parsing timestamps: {str(e)}', 'success': False},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Query the database
        queryset = Video.objects.filter(
            Q(start_timestamp__gte=starting) & Q(end_timestamp__lte=ending)
        ).values()
        
        
        print(starting)
        print(ending)

        if queryset.exists():
            return Response(
                {'data': list(queryset), 'message': 'Successfully fetched videos.', 'success': True},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'data': [], 'message': 'No videos found for the specified range.', 'success': True},
                status=status.HTTP_200_OK
            )