from django.shortcuts import render
from .models import Jobs



# Create your views here.
def homepage(request):
    return render(request=request,template_name="jobs/homepage.html",context={'job':Jobs.objects.all()} )