from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from .decorators import is_post_author
from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.PAGINATOR_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts_list = group.posts.all()
    paginator = Paginator(posts_list, settings.PAGINATOR_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(
        request,
        'group.html',
        {'group': group, 'page': page}
    )


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts_list = author.posts.all()
    posts_count = posts_list.count()
    paginator = Paginator(posts_list, settings.PAGINATOR_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    if request.user.is_authenticated:
        following = (
            Follow.objects.filter(user=request.user, author=author).exists())
    else:
        following = False
    follows = author.follower.count()
    followed_by = author.following.count()

    return render(request, 'profile.html',
                  {'author': author,
                   'posts_count': posts_count,
                   'page': page,
                   'following': following,
                   'follows': follows,
                   'followed_by': followed_by})


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    comments = post.comments.all()
    posts_count = post.author.posts.all().count()
    form = CommentForm()

    follows = post.author.follower.count()
    followed_by = post.author.following.count()

    return render(request, 'post.html',
                  {'author': post.author,
                   'posts_count': posts_count,
                   'post': post,
                   'form': form,
                   'comments': comments,
                   'follows': follows,
                   'followed_by': followed_by})


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return redirect(reverse_lazy('index'))

        return render(request, 'post_editing.html',
                      {'form': form, 'is_edit': False})

    form = PostForm()
    return render(request, 'post_editing.html', {'form': form})


@login_required
@is_post_author
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)

    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect(reverse_lazy('post', args=(username, post_id)))

    return render(request, 'post_editing.html',
                  {'form': form, 'post': post})


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.save()
    return redirect(reverse_lazy('post', args=(username, post_id)))


@login_required
def follow_index(request):
    follows = request.user.follower.all()
    followed_authors = [follow.author.id for follow in follows]
    post_list = Post.objects.filter(author__id__in=followed_authors)

    paginator = Paginator(post_list, settings.PAGINATOR_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'follow.html',
        {'page': page}
    )


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    if (author != user and not
            Follow.objects.filter(user=request.user, author=author).exists()):
        new_follow = Follow.objects.create(
            user=user,
            author=author,
        )
        new_follow.save()

    return redirect(reverse_lazy('profile', args=(username,)))


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    get_object_or_404(Follow, user=request.user, author=author).delete()
    return redirect(reverse_lazy('profile', args=(username,)))


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
