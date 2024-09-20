from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import DetailView
from django.views.generic.edit import DeleteView
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from .models import Post, Comment, Category  
from .forms import CommentForm, PostForm
import json


class PostList(generic.ListView):
    queryset = Post.objects.filter(status=1).order_by("-created_at")
    # This line of code tells Django to retrieve all posts with a status of 1 (approved) and order them
    # by the created_on field in descending order.
    template_name = "post_hub/index.html"
    paginate_by = 8
    
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

@csrf_exempt
# Exempt view from cross sit request forgery protection
def edit_comment(request, comment_id):
    if request.method == 'POST':
        try:
            comment = Comment.objects.get(id=comment_id, author=request.user)
# The comment the user is trying to edit is retrieved from the database.
            data = json.loads(request.body)
# The data from the request is loaded into a JSON object.
            comment.content = data['content']
# Comment content is updated with the new content from the request.
            comment.updated_at = timezone.now()
            comment.save()
            return JsonResponse({'success': True})
# A JSON response is returned to indicate that the comment was updated successfully.
        except Comment.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Comment not found or not authorized'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
# If the request method is not POST, a JSON response is returned to indicate that the request is invalid.
# I chose to use JSON responses for this view because it is an AJAX request and JSON is a common format for AJAX responses.


class DeleteComment(DeleteView):
    model = Comment
    success_url = reverse_lazy('home')

    def get_queryset(self):
        queryset = super().get_queryset()
# This line of code calls the get_queryset method of the parent class to retrieve the queryset.
# The queryset is used to filter the comments to only include comments by the current user.
        return queryset.filter(author=self.request.user)
# The author field of the comment is compared to the current user to filter the comments.
# The current user is retrieved from the request object and compared to the author field of the comment.
# This ensures that only the comments by the current user can be deleted.
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
# The get_object method is called to retrieve the comment to be deleted when the view is called.
        self.object.delete()
# The delete method is called on the comment object to delete the comment from the database.
        return JsonResponse({'success': True})


def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        # The data from the form is retrieved and stored in the form variable.
        # The request.FILES attribute is used to handle image uploads.
        
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            new_category_name = form.cleaned_data.get('new_category')
 # The new_category field is retrieved from the cleaned_data attribute of the form.
# The new_category field is used to create a new category if it does not already exist.
# cleaned_data attribute is used to retrieve the form data after it has been cleaned and validated.
# Django forms automatically clean and validate the data when the is_valid method is called.
            if new_category_name:
                category, created = Category.objects.get_or_create(category_name=new_category_name)
# This line of code retrieves the category object from the database or creates a new category if it does not already exist.
                post.category = category
                if created:
                    messages.success(request, f"A new category '{new_category_name}' was created.")

            post.save()
            messages.success(request, 'Your post has been tooted out successfully!')
            return redirect('post_detail', slug=post.slug)
            # The user is redirected to the post detail page for the newly created post.
        else:
            messages.error(request, 'There was an error creating your post. Please try again.')
            # If the form is not valid, an error message is displayed to the user.
            return redirect('create_post')
    else:
        form = PostForm()
        # If there is no POST request, an empty form is created.
    return render(request, 'post_hub/create_post.html', {'form': form})

    
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