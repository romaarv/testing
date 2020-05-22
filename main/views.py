from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse('<h1>Будем надеяться, что здесь скоро появится сайт для тестирования учеников!</h1>')