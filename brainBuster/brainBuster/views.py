from django.shortcuts import render

def home(request):
    """
    Render the homepage containing login, signup, and join quiz options.
    """
    return render(request, 'home.html')
