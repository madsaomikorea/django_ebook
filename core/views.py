from django.shortcuts import render

def csrf_failure(request, reason=""):
    context = {'message': 'Some text'}
    return render(request, '403.html', context, status=403)
