from django.shortcuts import render

def handler404(request, exception):
    context = {}
    response = render(request, "404.html", context=context)
    response.status_code = 404
    return response

def handler500(request):
    context = {}
    response = render(request, "500.html", context=context)
    response.status_code = 500
    return response

def handler503(request):
    context = {}
    response = render(request, "503.html", context=context)
    response.status_code = 503
    return response

def handler400(request, exception):
    context = {}
    response = render(request, "400.html", context=context)
    response.status_code = 400
    return response

def my_view(request):
    return render(request, "base.html")