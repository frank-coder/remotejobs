from django.db import models

# Create your models here.

class Jobs(models.Model):

    #title = models.CharField(max_length=200)
    text = models.TextField()
    created_on = models.DateTimeField()
    link = models.URLField()

    def __str__(self):
        return self.text
    