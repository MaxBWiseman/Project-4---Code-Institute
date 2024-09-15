from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.views import generic
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import DetailView
from django.urls import reverse
from .models import Post, Comment, Category  
from .forms import CommentForm


class PostList(generic.ListView):
    queryset = Post.objects.filter(status=1).order_by("-created_at")
    # This line of code tells Django to retrieve all posts with a status of 1 (approved) and order them
    # by the created_on field in descending order.
    template_name = "post_hub/index.html"
    paginate_by = 3
    
 # django automatically sets the context_object_name attribute to object_list.
    # e.g "post_list" is the context_object_name, this becomes our iterator
    # in the templates to show all published posts in order of date posted.

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
# The get_context_data method is overridden to add the categories to the context.
        context['categories'] = Category.objects.all()
# The categories are retrieved and added to the context.
        return context
# By overriding the get_context_data method, you can add the categories to the context in a more
# standard and efficient way. This approach ensures that the categories are available in the template
# without creating a separate method for retrieving category data.
 

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status=True)
# Grab all comments related to the post with status approved

    allcomments = post.comments.filter(status=True)
# The comments are filtered to only include approved comments.
# "comments" is the related name of the ForeignKey in the Comment model.
    page = request.GET.get('page', 1)
# This line of code retrieves the page number from the GET request.
# Djangos pagination system includes the page paramenter in the URL, so the page number can be retrieved
    paginator = Paginator(allcomments, 10)
# The comments are paginated with 10 comments per page. Using the Paginator class from Django.
    try:
        comments = paginator.page(page)
# The page method is called on the paginator object to retrieve the comments for the requested page. 
    except PageNotAnInteger:
        comments = paginator.page(1)
    except EmptyPage:
        comments = paginator.page(paginator.num_pages)
# The PageNotAnInteger and EmptyPage exceptions are handled to ensure that the page number is valid.
    user_comment = None
# this is to store the comment that the user is going to post

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
# The data from the form is retrieved and stored in the comment_form variable.
        if comment_form.is_valid():
            user_comment = comment_form.save(commit=False)
# The comment is saved to the database but not committed.
# so we may manipulate the comment before saving it to the database
            user_comment.post = post
# This is to associate the comment with the post.
            user_comment.author = request.user
# This is to associate the comment with the user that posted it.
            user_comment.save()
            return HttpResponseRedirect(reverse('post_detail', args=[post.slug]))
#We use args to pass the slug of the post to the URL pattern. To redirect to the correct post detail page.
    else:
        comment_form = CommentForm()
# If there is no POST request, an empty comment form is created.
    return render(request, 'post_hub/post_detail.html', {'post': post, 'comments': comments, 'comment_form': comment_form, 'allcomments': allcomments})
# The post, comments, comment_form, and allcomments are passed to the template.


    
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'post_hub/category_list.html', {'categories': categories})

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'post_hub/category_detail.html'
    context_object_name = 'category'

    def get_object(self):
        slug = self.kwargs.get("slug")
        return get_object_or_404(Category, slug=slug)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
# The get_context_data method is overridden to add the posts in the category to the context.
        category = self.get_object()
# The category object is retrieved from the context.
        context['posts'] = Post.objects.filter(category=category, status=1).order_by("-created_at")
# The posts in the category are retrieved and added to the context.
        return context