from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage,\
    PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count
from django.views.generic import (TemplateView, ListView,
                                  DetailView, CreateView,
                                  UpdateView, DeleteView)


# create Post Test here

class CreatePostView(CreateView):

    redirect_field_name = 'blog/post/create.html'

    model = Post


# Create your views here.


# class listview this is best way for views posts

class PostListView(ListView):

    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_list(request, tag_slug=None):  # we are add tag otion after comment system not in first

    object_list = Post.published.all()

    # tag here

    tag = None

    if tag_slug:

        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    # paginator

    paginator = Paginator(object_list, 3)  # 3 post each page

    page = request.GET.get('page')

    try:

        posts = paginator.page(page)

    except PageNotAnInteger:

        # if page is not an integer deliver the first page

        posts = paginator.page(1)

    except EmptyPage:

        # if page out of range deliver last page is result

        posts = paginator.page(paginator.num_pages)

    return render(request, 'blog/post/list.html', {'page': page, 'posts': posts, 'tag': tag})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)


# here def for comments

# list of acxtive the comments for this pos

    comments = post.comments.filter(active=True)

    new_comment = None

    if request.method == 'POST':

        # A comment was posted
        comment_form = CommentForm(data=request.POST)

        if comment_form.is_valid():

            # create comment object but dont to database yet
            new_comment = comment_form.save(commit=False)

            # Assign the current post to the comment
            new_comment.post = post

            # save the comment to the database
            new_comment.save()

    else:

        comment_form = CommentForm()

    # list of similar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids)\
                                  .exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags'))\
        .order_by('-same_tags', '-publish')[:4]

    return render(request,
                  'blog/post/detail.html',
                  {'post': post,
                      'comments': comments,
                      'new_comment': new_comment,
                      'comment_form': comment_form,
                      'similar_posts': similar_posts})


# def for send post to email

def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                      f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'aposara.acp@gmail.com', [cd['to']])
            sent = True

    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form,
                                                    'sent': sent})

# post similar
