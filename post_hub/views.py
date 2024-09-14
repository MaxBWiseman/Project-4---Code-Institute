from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.views.generic import DetailView
from .models import Post, Category, Comment
from .forms import CommentForm, ReplyForm

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
    comment_form = CommentForm()
    reply_form = ReplyForm()

    if request.method == 'POST':
        if 'submit_comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                return redirect('post_hub/post_detail', slug=slug)
        elif 'submit_reply' in request.POST:
            reply_form = ReplyForm(request.POST)
            if reply_form.is_valid():
                reply = reply_form.save(commit=False)
                reply.post = post
                reply.author = request.user
                reply.save()
                return redirect('post_hub/post_detail', slug=slug)

    comments = post.comments.filter(parent__isnull=True)

    return render(request, 'post_hub/post_detail.html', {
        'post': post,
        'comment_form': comment_form,
        'reply_form': reply_form,
        'comments': comments,
    })

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