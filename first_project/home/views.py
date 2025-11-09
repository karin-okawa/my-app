from django.shortcuts import render
from django.http import HttpResponse
from django.views import View

def index(request):
    return HttpResponse('<h1>ポートフォリオ</h1>')


def user_page(request, user_name):
    print(type(user_name),user_name)
    return HttpResponse(f'<h1>{user_name} Page</h1>')

class IndexView(View):
    def get(self, request):
        return render(request, "home/index.html")

index = IndexView.as_view()
    