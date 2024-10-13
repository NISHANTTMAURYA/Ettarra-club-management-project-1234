from django.shortcuts import render, redirect

def index(request):
    return render (request, 'index.html')


def review(request):
    return render (request, 'review.html')