from django.db import models

class Video(models.Model):
    name = models.CharField(max_length=255)
    video_file = models.FileField(upload_to='videos/')
    start_timestamp = models.DateTimeField()
    end_timestamp = models.DateTimeField()

    def __str__(self):
        return self.name
