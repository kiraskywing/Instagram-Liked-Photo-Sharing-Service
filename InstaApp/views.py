from django.shortcuts import render
from django.views.generic import TemplateView, ListView

from InstaApp.models import Post

# Create your views here.
class HelloWorld(TemplateView):
    template_name = 'test.html'

class PostsView(ListView):
    model = Post
    template_name = 'index.html'