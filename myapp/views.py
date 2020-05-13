from django.shortcuts import render, redirect  # HttpResponse,
from django.db.models import Q  # allows complex query lookups
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist

from . import models
from . import forms


# Create your views here.
def index(request, page=0):
    context = {
        "title": "ODIT - On Demand IT",
        "info": "A new way to find IT professionals.",
        "how": "How it works: ",
        "desc": "Send in a request --> A registered ODITer who has the skills needed receives the request --> They help out. ",
    }
    if request.user.is_authenticated:
        context["is_technician"] = models.Profile.objects.get(user__exact=request.user).user_type
    return render(request, "index.html", context=context)


@login_required
def submit(request):
    if request.method == "POST":
        form = forms.IssueForm(request.POST)
        if form.is_valid():
            form.save(request.user)  # pass in user for foreign key relationship
            form = forms.IssueForm()
    else:
        form = forms.IssueForm()

    context = {
        "title": "ODIT - Submit Request",
        "form": form,
        "is_technician": models.Profile.objects.get(user__exact=request.user).user_type,
    }
    return render(request, "submit.html", context=context)


@login_required
def viewissues(request):
    if request.method == "POST":
        form = forms.IssueFilter(request.POST)
        if form.is_valid():
            issues_list = models.Issue_Model.objects.all()
            if (form.cleaned_data['keyword']):
                issues_list = issues_list.filter(
                    Q(title__contains=form.cleaned_data['keyword']) |
                    Q(description__contains=form.cleaned_data['keyword']) |
                    Q(assigned_user__username__contains=form.cleaned_data['keyword']) |
                    Q(affected_user__username__contains=form.cleaned_data['keyword'])
                )
            if (form.cleaned_data['issue_type']):
                issues_list = issues_list.filter(
                    Q(issue_type__exact=form.cleaned_data['issue_type'])
                )
        else:
            form = forms.IssueFilter()
            issues_list = models.Issue_Model.objects.all()
    else:
        form = forms.IssueFilter()
        issues_list = models.Issue_Model.objects.all()

    context = {
        "title": "ODIT - View Requests",
        "issues_list": issues_list,
        "form": form,
        "is_technician": models.Profile.objects.get(user__exact=request.user).user_type,
    }
    return render(request, "viewissues.html", context=context)


@login_required
def viewmyissues(request):
    issues_list = models.Issue_Model.objects.filter(assigned_user=request.user)
    if request.method == "POST":
        form = forms.IssueFilter(request.POST)
        if form.is_valid():
            if (form.cleaned_data['keyword']):
                issues_list = issues_list.filter(
                    Q(title__contains=form.cleaned_data['keyword']) |
                    Q(description__contains=form.cleaned_data['keyword']) |
                    Q(affected_user__username__contains=form.cleaned_data['keyword'])
                )
            if (form.cleaned_data['issue_type']):
                issues_list = issues_list.filter(
                    Q(issue_type__exact=form.cleaned_data['issue_type'])
                )
        else:
            form = forms.IssueFilter()
    else:
        form = forms.IssueFilter()

    context = {
        "title": "ODIT - View Assignments",
        "issues_list": issues_list,
        "form": form,
        "is_technician": models.Profile.objects.get(user__exact=request.user).user_type,
    }
    return render(request, "viewmyissues.html", context=context)


@login_required
def self_assign(request, issue_id):
    if models.Profile.objects.get(user__exact=request.user).user_type:  # confirm that user is a technician
        if request.user.is_authenticated:
            this_issue = models.Issue_Model.objects.get(id__exact=issue_id)
            this_issue.assigned_user = request.user
            this_issue.save()
    return redirect("/viewissues.html")


def about(request):
    context = {
        "title": "ODIT - About",
    }
    if request.user.is_authenticated:
        context["is_technician"] = models.Profile.objects.get(user__exact=request.user).user_type
    return render(request, "aboutodit.html", context=context)


def register(request):
    if request.method == "POST":
        form_instance = forms.RegistrationForm(request.POST)
        if form_instance.is_valid():
            form_instance.save()
            return redirect("/login/")
    else:
        form_instance = forms.RegistrationForm()
    context = {
        "title": "ODIT - Register",
        "form": form_instance,
    }
    return render(request, "registration/register.html", context=context)


def logoff(request):
    logout(request)
    return redirect("/login")


@login_required
def profile_page(request):
    this_user = models.Profile.objects.get(user__exact=request.user)
    context = {
        "title": "ODIT - {}".format(request.user.username),
        "user_name": request.user.username,
        "bio": this_user.bio,
        "location": this_user.location,
        "email": request.user.email,
        "is_technician": this_user.user_type,
    }
    return render(request, "profile.html", context=context)


@login_required
def edit_profile(request):
    this_user = models.Profile.objects.get(user__exact=request.user)
    if request.method == "POST":
        form_instance = forms.ProfileForm(request.POST)
        if form_instance.is_valid():
            form_instance.save(request.user.id)
            return redirect("/profile.html")
    else:
        if this_user.user_type:
            form_instance = forms.ProfileForm(
                initial={
                    'location': this_user.location,
                    'bio': this_user.bio,
                    'email': request.user.email,
                    'user_name': request.user.username
                }
            )
        else:
            form_instance = forms.ProfileFormNontech(
                initial={
                    'email': request.user.email,
                    'user_name': request.user.username
                }
            )
    context = {
        "title": "ODIT - Edit Profile".format(request.user.username),
        "form": form_instance,
        "is_technician": this_user.user_type,
    }
    return render(request, "editprofile.html", context=context)


@login_required
def become_technician(request):
    if request.user.is_authenticated:
        this_user = models.Profile.objects.get(user__exact=request.user)
        this_user.user_type = True
        this_user.save()
    return redirect("/profile.html")


@login_required
def view_technicians(request):
    if request.method == "POST":
        form = forms.ProfileFilter(request.POST)
        if form.is_valid():
            profile_list = models.Profile.objects.filter(user_type=True)
            if (form.cleaned_data['keyword']):
                profile_list = profile_list.filter(
                    Q(bio__contains=form.cleaned_data['keyword']) |
                    Q(user__username__contains=form.cleaned_data['keyword']) |
                    Q(location__contains=form.cleaned_data['keyword'])
                )
            if (form.cleaned_data['name']):
                profile_list = profile_list.filter(user__username__contains=form.cleaned_data['name'])
            if (form.cleaned_data['location']):
                profile_list = profile_list.filter(
                    Q(location__contains=form.cleaned_data['location'])
                )
        else:
            form = forms.ProfileFilter()
            profile_list = models.Profile.objects.filter(user_type=True)
    else:
        form = forms.ProfileFilter()
        profile_list = models.Profile.objects.filter(user_type=True)

    context = {
        "title": "ODIT - View Requests",
        "profile_list": profile_list,
        "form": form,
        "is_technician": models.Profile.objects.get(user__exact=request.user).user_type,
    }
    return render(request, "viewtechnicians.html", context=context)


@login_required
def view_profile(request, user_id):
    this_user = models.Profile.objects.get(user__exact=request.user)
    try:
        view_user = models.Profile.objects.get(user__id__exact=user_id)
    except ObjectDoesNotExist:
        return redirect("/viewtechnicians.html")
    if request.method == "POST":
        form_instance = forms.AddReviewForm(request.POST)
        if form_instance.is_valid():
            form_instance.save(this_user.user.id, view_user.user.id)
            return redirect("/viewprofile/{}".format(view_user.id))
    else:
        if this_user != view_user and (not models.Review.objects.filter(writer=this_user.user).filter(subject=view_user.user).exists()) and models.Issue_Model.objects.filter(affected_user=this_user.user).filter(assigned_user=view_user.user).exists():
            form = forms.AddReviewForm()
        else:
            form = False
        context = {
            "title": "ODIT - {}".format(view_user.user.username),
            "user_name": view_user.user.username,
            "bio": view_user.bio,
            "location": view_user.location,
            "email": view_user.user.email,
            "form": form,
            "reviews_list": models.Review.objects.filter(subject=view_user.user),
            "rating": view_user.rating_avg,
            "is_technician": this_user.user_type,
        }
        print(list(context['reviews_list']))
        return render(request, "viewprofile.html", context=context)


@login_required
def viewmysubmittedissues(request):
    issues_list = models.Issue_Model.objects.filter(affected_user=request.user)
    if request.method == "POST":
        form = forms.IssueFilter(request.POST)
        if form.is_valid():
            if (form.cleaned_data['keyword']):
                issues_list = issues_list.filter(
                    Q(title__contains=form.cleaned_data['keyword']) |
                    Q(description__contains=form.cleaned_data['keyword']) |
                    Q(affected_user__username__contains=form.cleaned_data['keyword'])
                )
            if (form.cleaned_data['issue_type']):
                issues_list = issues_list.filter(
                    Q(issue_type__exact=form.cleaned_data['issue_type'])
                )
        else:
            form = forms.IssueFilter()
    else:
        form = forms.IssueFilter()

    context = {
        "title": "ODIT - Your Submitted Issues",
        "issues_list": issues_list,
        "form": form,
        "is_technician": models.Profile.objects.get(user__exact=request.user).user_type,
    }
    return render(request, "viewmysubmittedissues.html", context=context)


@login_required
def edit_review(request, id):
    this_user = models.Profile.objects.get(user__exact=request.user)
    try:
        this_review = models.Review.objects.get(id__exact=id)
        view_user = models.Profile.objects.get(user__exact=this_review.subject)
    except ObjectDoesNotExist:
        return redirect("/viewtechnicians.html")
    if request.method == "POST":
        form_instance = forms.EditReviewForm(request.POST)
        if form_instance.is_valid():
            form_instance.save(id)
            return redirect("/viewprofile/{}".format(view_user.user.id))
    else:
        if this_user == models.Review.objects.get(id__exact=id).writer.profile:
            form = forms.EditReviewForm(
                initial={
                    'rating': this_review.rating,
                    'review': this_review.review
                }
            )
            context = {
                "title": "ODIT - Edit Review for {}".format(view_user.user.username),
                "form": form,
                "id": view_user.user.id,
                "is_technician": this_user.user_type,
            }
            return render(request, "editreview.html", context=context)
        else:
            return redirect("/viewprofile/{}".format(view_user.user.id))


@login_required
def resolve_ticket(request, id):
    try:
        this_ticket = models.Issue_Model.objects.get(id__exact=id)
    except ObjectDoesNotExist:
        return redirect("/viewmyissues.html")
    if request.method == "POST":
        form_instance = forms.ResolveIssueForm(request.POST)
        if form_instance.is_valid():
            form_instance.save(id)
            return redirect("/viewmyissues.html")
    else:
        if this_ticket == models.Issue_Model.objects.get(id__exact=id):
            form = forms.ResolveIssueForm(
                initial={
                    'Resolved?': this_ticket.is_solved,
                    'Resolution': this_ticket.resolution
                }
            )
            context = {
                "title": "ODIT - Resolve Ticket",
                "form": form,
                "id": this_ticket,
            }
            return render(request, "editticket.html", context=context)
        else:
            return redirect("/viewmyissues")


@login_required
def edit_ticket(request, id):
    try:
        this_ticket = models.Issue_Model.objects.get(id__exact=id)
    except ObjectDoesNotExist:
        return redirect("/viewmysubmittedissues.html")
    if request.method == "POST":
        form_instance = forms.EditIssueForm(request.POST)
        if form_instance.is_valid():
            form_instance.save(id)
            return redirect("/viewmysubmittedissues.html")
    else:
        if this_ticket == models.Issue_Model.objects.get(id__exact=id):
            form = forms.EditIssueForm(
                initial={
                    'title': this_ticket.title,
                    'description': this_ticket.description,
                    'issue_type': this_ticket.issue_type
                }
            )
            context = {
                "title": "ODIT - Edit Ticket",
                "form": form,
                "id": this_ticket,
            }
            return render(request, "editticket.html", context=context)
        else:
            return redirect("/viewmysubmittedissues.html")
