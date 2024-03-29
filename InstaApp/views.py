from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from InstaApp.models import Post, Like, InstaUser, UserConnection, Comment
from InstaApp.forms import CustomUserCreationForm

from annoying.decorators import ajax_request

# Create your views here.
class HelloWorld(TemplateView):
    template_name = 'test.html'

class PostsView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'index.html'
    login_url = 'login'

    def get_queryset(self):
        current_user = self.request.user
        users = {current_user}
        for conn in UserConnection.objects.filter(creator=current_user).select_related('following'):
            users.add(conn.following)
        return Post.objects.filter(author__in=users).order_by('-posted_on')

class ExploreView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'explore.html'
    login_url = 'login'

    def get_queryset(self):
        return Post.objects.all().order_by('-posted_on')[:20]

class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'post_detail.html'
    login_url = 'login'

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'post_create.html'
    fields = ['title', 'image']
    login_url = 'login'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = 'post_update.html'
    fields = ['title']
    login_url = 'login'

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy("posts")
    login_url = 'login'

class SignUp(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'signup.html'
    success_url = reverse_lazy("login")

class UserDetailView(LoginRequiredMixin, DetailView):
    model = InstaUser
    template_name = 'user_detail.html'
    login_url = 'login'

class EditProfile(LoginRequiredMixin, UpdateView):
    model = InstaUser
    template_name = 'edit_profile.html'
    fields = ['profile_pic', 'username']
    login_url = 'login'

class FollowerProfile(LoginRequiredMixin, ListView):
    model = InstaUser
    template_name = 'connections.html'
    login_url = 'login'

    def get_queryset(self):
        user_pk = self.kwargs['pk']
        this_user = InstaUser.objects.filter(pk=user_pk)
        followers = set()
        for conn in UserConnection.objects.filter(following__in=this_user):
            followers.add(conn.creator.pk)
        return InstaUser.objects.filter(pk__in=followers)

class FollowingProfile(LoginRequiredMixin, ListView):
    model = InstaUser
    template_name = 'connections.html'
    login_url = 'login'

    def get_queryset(self):
        following = set()
        connection_set = UserConnection.objects.filter(creator__pk=self.kwargs['pk'])

        for connection in connection_set:
            following.add(connection.following.pk)
        return InstaUser.objects.filter(pk__in=following)

@ajax_request
def addLike(request):
    post_pk = request.POST.get('post_pk')
    post = Post.objects.get(pk=post_pk)
    try:
        like = Like(post=post, user=request.user)
        like.save()
        result = 1
    except Exception as e:
        like = Like.objects.get(post=post, user=request.user)
        like.delete()
        result = 0

    return {
        'result': result,
        'post_pk': post_pk
    }

@ajax_request
def toggleFollow(request):
    current_user = InstaUser.objects.get(pk=request.user.pk)
    follow_user_pk = request.POST.get('follow_user_pk')
    follow_user = InstaUser.objects.get(pk=follow_user_pk)

    try:
        if current_user != follow_user:
            if request.POST.get('type') == 'follow':
                connection = UserConnection(creator=current_user, following=follow_user)
                connection.save()
            elif request.POST.get('type') == 'unfollow':
                UserConnection.objects.filter(creator=current_user, following=follow_user).delete()
            result = 1
        else:
            result = 0
    except Exception as e:
        print(e)
        result = 0

    return {
        'result': result,
        'type': request.POST.get('type'),
        'follow_user_pk': follow_user_pk
    }

@ajax_request
def addComment(request):
    comment_text = request.POST.get('comment_text')
    post_pk = request.POST.get('post_pk')
    post = Post.objects.get(pk=post_pk)
    commenter_info = {}

    try:
        comment = Comment(comment=comment_text, user=request.user, post=post)
        comment.save()

        username = request.user.username
        user_pk = request.user.pk
        user_profile_pic = str(request.user.profile_pic)

        commenter_info = {
            'user_pk': user_pk,
            'username': username,
            'user_profile_pic': user_profile_pic,
            'comment_text': comment_text
        }

        result = 1
    except Exception as e:
        print(e)
        result = 0

    return {
        'result': result,
        'post_pk': post_pk,
        'commenter_info': commenter_info
    }