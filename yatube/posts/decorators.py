from functools import wraps

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy

from .models import Post


def is_post_author(func):
    """Проверяет, является ли текущий пользователь автором поста."""
    @wraps(func)
    def wrapper(request, username, post_id, *args, **kwargs):
        post = get_object_or_404(Post, id=post_id)
        if request.user == post.author:
            return func(request, username, post_id, *args, **kwargs)
        return redirect(reverse_lazy('post', args=(username, post_id)))
    return wrapper
