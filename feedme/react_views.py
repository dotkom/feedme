from django.shortcuts import render


def react_index(request):
    return render(request, 'feedme/react/index.html', {})