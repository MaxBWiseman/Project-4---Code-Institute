from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.views.generic import DetailView
from .models import Post, Category, Comment

# Create your views here.

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
    post = get_object_or_404(Post, slug=slug)
# This line of code retrieves the post with the given slug from the database.
    if request.method == 'POST':
# If user requests to post a comment, the code below will be executed.
        content = request.POST.get('comment-box')
# The content of the comment is retrieved from the form.
        parent_id = request.POST.get('parent-id')
# The parent_id is retrieved from the form.
        parent_comment = None
# The parent_comment variable is set to None. Because the comment is not a reply to another comment.
        if parent_id:
            parent_comment = Comment.objects.get(id=parent_id)
# If the parent_id exists, the parent_comment variable is set to the comment with the given id.
        Comment.objects.create(post=post, author=request.user, content=content, parent=parent_comment)
# The comment is created with the post, author, content, and parent_comment.
        return redirect('post_hub/post_detail', slug=slug)
# The user is redirected to the post detail page.
    return render(request, 'post_hub/post_detail.html', {'post': post})
# The post detail page is rendered with the post object.

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