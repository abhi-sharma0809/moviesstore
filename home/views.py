from django.shortcuts import render

def index(request):
    template_data = {}
    template_data['title'] = 'Georgia Tech Movie Store'
    return render(request, 'home/index.html', {'template_data': template_data})

def about(request):
    template_data = {}
    template_data['title'] = 'About - Georgia Tech Movie Store'
    return render(request, 'home/about.html', {'template_data': template_data})