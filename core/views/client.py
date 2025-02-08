from django.shortcuts import render

def index(request):
    aux = {
        
    }
    if request.method == 'POST':
        pass

    return render(request, "core/client/index.html", aux)


