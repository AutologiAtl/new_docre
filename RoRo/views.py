from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def Hello(requests):
    return HttpResponse("Hey! Manish this side")