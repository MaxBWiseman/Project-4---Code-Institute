from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.db import IntegrityError, transaction
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import DetailView
from django.views.generic.edit import DeleteView
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from .models import Post, Comment, Category, Vote
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

@login_required
def vote(request):
    """
    This view function interacts with the Vote model to create, update, or delete
    vote records in the database based on the data received from the AJAX requests in script.js
    linked with the urls.py file.
    """
    if request.method == 'POST':
        data = json.loads(request.body)
# The data from the request is loaded into a JSON object.
        post_id = data.get('post_id')
        comment_id = data.get('comment_id')
        is_upvote = data.get('is_upvote')
# post_id, comment_id, and is_upvote are retrieved from the JSON object.
# comment_id is retrieved using the get method to handle when the request isnt for a comment.
# updated all to .get to avoid keyError
        if is_upvote is None:
            messages.error(request, 'A vote choice is required')
            return JsonResponse({'success': False})
# If is_upvote is not provided, a JSON response is returned to indicate that the request has failed.
        user = request.user
        try:
            with transaction.atomic():
# The transaction.atomic() method is used to ensure that either all of the code encapsulated in this view succeeds or none of it does.
# This ensures that all operations are either committed or rolled back together. If an error occurs during the view function,
# the transaction is rolled back and the database is restored to its previous state. This ensures data integrity.
# I learned of this here when browsing for ways to make sure votes are not placed multiple times
# https://dev.to/rockandnull/atomic-transactions-in-django-19m5
                if post_id:
# If post_id exists, the vote is for a post.
                    post = get_object_or_404(Post, id=post_id)
# The post object to associate with is retrieved from the database using the post_id.
                    vote = post.votes.filter(user=user).first()
# The vote object is retrieved from the database using the post_id.
# The first method is used to retrieve the first vote object for the user
# because there should only be one vote per user.
                elif comment_id:
# If comment_id exists, the vote is for a comment.
                    comment = get_object_or_404(Comment, id=comment)
                    vote = comment.votes.filter(user=user).first()
# The vote object is retrieved from the database using the comment_id.
                else:
                    messages.error(request, 'Invalid request')
                    return JsonResponse({'success': False})
# If neither post_id nor comment_id exists, a JSON response is returned to indicate that the request has failed.

                if vote:
# The vote we grabbed above
                    if vote.is_upvote == is_upvote:
                        vote.delete()
# If the vote exists and the is_upvote field is the same as the request, the vote is deleted.
                    else:
                        vote.is_upvote = is_upvote
                        vote.save()
# If the vote exists and the is_upvote field is different from the request, the is_upvote field is updated.
# This is for if the user wants to change their vote.
                else:
                    if post_id:
                        post.votes.create(user=user, is_upvote=is_upvote)
# If the vote does not exist, a new vote is created with the user and is_upvote field.
                    elif comment_id:
                        comment.votes.create(user=user, is_upvote=is_upvote)
# .create() is a great way to create a new object and save it to the database in one step.
# The new vote object is saved to the database with the user and is_upvote values.
# https://stackoverflow.com/questions/54493476/how-to-save-object-in-django-database
            messages.success(request, 'Your vote has been recorded.')
            return JsonResponse({'success': True})
        except IntegrityError:
            messages.error(request, 'You have already voted on this item.')
            return JsonResponse({'success': False})
        except Exception as e:
            messages.error(request, str(e))
            return JsonResponse({'success': False})

    messages.error(request, 'Invalid request method')
    return JsonResponse({'success': False})



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
        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to post a comment.')
            return redirect('account_login')
        comment_form = CommentForm(request.POST)
# The data from the form is retrieved and stored in the comment_form variable.
        if comment_form.is_valid():
            try:
                with transaction.atomic():
# I have learned above that transaction.atomic() is great to keep the database in a consistent state.
# The method is used to ensure that either all of the code encapsulated in this view succeeds or none of it does.
                    user_comment = comment_form.save(commit=False)
# The comment is saved to the database but not committed.
# so we may manipulate the comment before saving it to the database
                    user_comment.post = post
# This is to associate the comment with the post.
                    user_comment.author = request.user
# This is to associate the comment with the user that posted it.
                    user_comment.save()
                    messages.success(request, 'Your comment has been posted successfully!')
                    return HttpResponseRedirect(reverse('post_detail', args=[post.slug]) + '?comment_posted=true#comments-section')
# The user is redirected to the same page their comment is posted with a query parameter to indicate that the
# screen should scroll to the comment section for good user experience. The + '?comment_posted=true#comments-section' is added to the URL.
# If it exists, the page will scroll to the comments section when the page is loaded through "script.js".
# the question mark is used to add a query parameter to the URL.
            except IntegrityError:
# This exception comes from transaction.atomic() and is raised when there is an integrity error in the database.
                messages.error(request, 'There was an error posting your comment. Please try again.')
                return HttpResponseRedirect(reverse('post_detail', args=[post.slug]))
# The user is redirected to the post detail page with an error message if there is an integrity error
    else:
        comment_form = CommentForm()
# If there is no POST request, an empty comment form is created.

    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'allcomments': allcomments,
        'total_upvotes': post.total_upvotes(),
        'total_downvotes': post.total_downvotes(),
        'comment_votes': {comment.id: {'upvotes': comment.total_upvotes(),
                                       'downvotes': comment.total_downvotes()}
                          for comment in allcomments}
    }
    return render(request, 'post_hub/post_detail.html', context)
# total_upvotes and total_downvotes are added to the context to display the total number of upvotes and downvotes for the post.
# comment_votes is added to the context to display the total number of upvotes and downvotes for each comment using a dictionary comprehension.

def edit_comment(request, comment_id):
    if request.method == 'POST':
        try:
            with transaction.atomic():
# The transaction.atomic() method is used to ensure that either all of the code in this view succeeds or none of it does.
                comment = Comment.objects.get(id=comment_id, author=request.user)
# The comment the user is trying to edit is retrieved from the database.
                data = json.loads(request.body)
# The data from the request is loaded into a JSON object.
                comment.content = data['content']
# Comment content is updated with the new content from the request.
                comment.save()
                messages.success(request, 'Your comment has been updated.')
                return JsonResponse({'success': True})
# A JSON response is returned to indicate that the comment was updated successfully.
        except Comment.DoesNotExist:
            messages.error(request, 'Comment not found or not authorized')
            return JsonResponse({'success': False})
    messages.error(request, 'Invalid request method')
    return JsonResponse({'success': False})
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

@login_required
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