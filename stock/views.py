from django.shortcuts import render

# Create your views here.

def home(request):
    msg ="안녕하세요"
    return render(request,"stockmain.html",{'msg':msg})