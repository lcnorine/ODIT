from django.shortcuts import render, HttpResponse
from . import models
from . import forms

# Create your views here.
def index(request, page=0):

    context = {
        "title":"On Demand IT",
        "info":"A new way to find IT professionals.",
        "how":"How IT works: ",
        "desc":"Send in a request --> A registered ODITer who has the skills needed receives the request --> They help out. ",
    }
   
    return render(request, "index.html", context=context)

def submit(request):
    if request.method == "POST":
        form = forms.IssueForm(request.POST)
        if form.is_valid():
            form.save()
            form = forms.IssueForm()
    else:
        form = forms.IssueForm()

    context = {
        "title":"ODIT - Make Request",
        "form":form
    }
    return render(request, "submit.html", context=context)

def viewissues(request):
    
    issues_list = models.Issue_Model.objects.all()

    context = {
        "title":"ODIT - View Requests",
        "issues_list":issues_list,
    }
    return render(request, "viewissues.html", context=context)

def about(request):
    return render(request, "aboutodit.html")