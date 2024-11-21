function formExit() {
    $("#newForm").remove();
}
/* This function removes the form when formExit is invoked */

function grabOne(id) {
    if ($("#newForm").length) {
        $("#newForm").remove();
    }
    /* This is to make sure only one reply form can be viewed at one time
    This function is attached to the reply button */

    // Extract the author information from the comment-author span
    var author = $(`#comment-${id} .comment-author`).text().replace('By ', '');
    var csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

/* Reply form */
var formHtml = `
<form id="newForm" class="form-insert py-2" method="post" enctype='multipart/form-data'>
     <div class="d-flex justify-content-between">
         <h2>You are Replying to: ${author}</h2>
         <div>
             <button type="button" class="btn btn-danger me-2" onclick="formExit()">Close</button>
         </div>
     </div>
     <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
     <input type="hidden" name="form_type" value="comment_form">
     <select name="parent" class="d-none" id="id_parentt">
         <option value="${id}" selected>${id}</option>
     </select>
     <label for="id_content">Content:</label>
     <textarea name="content" cols="40" rows="5" class="form-control" required id="id_content"></textarea>
     <input type="file" name="image" class="form-control mt-2" id="id_image">
     <hr>
     <div class="d-flex justify-content-center">
         <button type="submit" class="btn btn-primary btn-lg btn-block">Submit</button>
     </div>
 </form>
`;
    /* This is the form that will be inserted after the comment that is being replied to when the reply button is clicked */

    $(`#comment-${id}`).after(formHtml);
    /* This is to insert the form after the comment that is being replied to
    using the id we grabbed in the grabOne function to associate the reply with the comment */
}

document.addEventListener('DOMContentLoaded', function() {
    // Hide messages modals inside the footer after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            alert.style.display = 'none';
        });
    }, 5000);

    const dayNightSwitch = document.getElementById('day-night');

    // Check state of day-night switch
    if (localStorage.getItem('dayNightSwitch') === 'true') {
        dayNightSwitch.checked = true;
        document.body.classList.add('night-mode');
    } else {
        dayNightSwitch.checked = false;
        document.body.classList.remove('night-mode');
    }

    dayNightSwitch.addEventListener('change', function() {
        localStorage.setItem('dayNightSwitch', dayNightSwitch.checked);
        if (dayNightSwitch.checked) {
            document.body.classList.add('night-mode');
        } else {
            document.body.classList.remove('night-mode');
        }
    })
});

function pageRefresh() {
    location.reload();
}

function confirmDeletePost(postId) {
    const modal = document.getElementById('deleteModal');
    const confirmBtn = document.getElementById('confirmDeleteBtn');
    modal.style.display = 'block';
    confirmBtn.onclick = function() {
        deletePost(postId);
    }
}

function confirmDelete(commentId) {
    const modal = document.getElementById('deleteModal');
    const confirmBtn = document.getElementById('confirmDeleteBtn');
    modal.style.display = 'block';
    confirmBtn.onclick = function() {
        deleteComment(commentId);
    };
}

function successModal() {
    const modal = document.getElementById('successModal');
    modal.style.display = 'block';
}

function cancelEditComment(commentId) {
    const commentContent = document.getElementById('comment-content-' + commentId);
    const editForm = document.getElementById('edit-comment-' + commentId);
    commentContent.style.display = 'block';
    editForm.style.display = 'none';
}

function editComment(commentId) {
    const commentContent = document.getElementById('comment-content-' + commentId);
    const editForm = document.getElementById('edit-comment-' + commentId);
    commentContent.style.display = 'none';
    editForm.style.display = 'block';
}

function submitEditComment(commentId) {
    return function(event) {
        event.preventDefault(); // Prevent the default form submission

        const commentBox = document.getElementById('edit-content-' + commentId);
        const commentText = commentBox.value;
        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
        // Collect edited comment data and token, associate with variables
        const formData = new FormData();
        //Create a new FormData object to send the data to the server
        formData.append('content', commentText);
        formData.append('csrfmiddlewaretoken', csrfToken);
        // Append the comment text and token to the FormData object

        const imageInput = document.querySelector(`#edit-comment-form-${commentId} input[name='image']`);
        // Grab the image input from the form
        if (imageInput && imageInput.files.length > 0) {
            // Check if an image has been uploaded
            formData.append('image', imageInput.files[0]);
            // Append the image to the FormData object
        } else {
            formData.append('remove_image', true);
            // If no image has been uploaded, append a remove_image key to the FormData object
        }

        fetch(`/edit_comment/${commentId}/`, {
            // The destination URL for the fetch request
            method: 'POST',
            body: formData,
            // POST the formData object to the server
        })
        .then(response => response.json())
        // First promise, turn the response into a JSON object
        .then(data => {
            // Second promise, use the JSON object to update the page
            if (data.success) {
                const commentNew = document.getElementById('edit-content-' + commentId);
                const commentOld = document.getElementById('comment-content-' + commentId);
                // Grab the new and old comment content elements
                commentOld.innerText = commentNew.value;
                // Update the comment content with the new content

                const commentImage = document.getElementById(`comment-image-${commentId}`);
                // Grab the comment image if exists
                if (commentImage) {
                    if (data.image) {
                        commentImage.src = data.image;
                        commentImage.style.display = 'block';
                        // If the image exists, update the image source and display it
                    } else {
                        commentImage.style.display = 'none';
                        // If the image does not exist, hide the image
                    }
                }

                // Hide the edit form and display the updated comment content
                cancelEditComment(commentId);
                console.log(`Comment ${commentId} updated successfully.`);
                successModal();
            } else {
                alert('Error updating comment: ' + data.error);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    };
}

function defaultFormSubmission(event) {
    // This function is empty as the form submission is handled by the server
}

function closeModal() {
    const modal = document.getElementById('deleteModal');
    const modal2 = document.getElementById('successModal');
    modal.style.display = 'none';
    modal2.style.display = 'none';
}

function deleteComment(commentId) {
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    fetch(`/comment/${commentId}/delete/`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('comment-' + commentId).remove();
            closeModal();
            successModal();
        } else {
            alert('Error deleting comment');
        }
    });
}

function deletePost(postId) {
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    fetch(`/post/${postId}/delete/`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            closeModal();
            successModal();
            setTimeout(() => {
                window.location.replace('/');
                }, 3000);
        } else {
            alert('Error deleting post');
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {

    function hideCreatedAtIfUpdated() {
        const comments = document.querySelectorAll("[id^='created-at-']");
// Grabs all elements with an id starting with 'created-at-'. id^ means to
// select all elements with an id that starts with the specified value

        comments.forEach(comment => {
// Our iterator function
            const commentId = comment.id.split('-')[2];
// We split the id of the comment to get the comment id, example: 'created-at-1'
            const createdAt = document.getElementById('created-at-' + commentId);
            const updatedAt = document.getElementById('updated-at-' + commentId);

            if (updatedAt) {
                const createdAtDate = new Date(createdAt.textContent.trim());
    // We convert the text content of the element to a date object, trimming any whitespace
                const updatedAtDate = new Date(updatedAt.textContent.replace('Edited: ', '').trim());
// remove the 'Edited: ' text so a clear date can be parsed by the date constructor
                if (createdAtDate.toDateString() !== updatedAtDate.toDateString()) {
// Check if dates are not the same
                    createdAt.style.display = 'none';
// Hide the created at date if the comment has been updated for good UX
                }
            }
        });
    }
    hideCreatedAtIfUpdated();
});
    
function votePost(postId, isUpvote) {
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
// Easily grab the CSRF token from the form
    fetch('/vote/', {
// sends a POST request to the /vote/ URL with the post_id and is_upvote
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({
// We use JSON.stringify to convert the data to a JSON string because fetch only accepts strings
            post_id: postId,
            is_upvote: isUpvote
        })
    })
    .then(response => response.json())
// we use the .then method to handle the response from the server and turn to a JSON object
// the fetch request returns a promise that turns into the response object
    .then(data => {
// data comes out as JSON and we can use it to update the page
        if (data.success) {
            location.reload();
// I have only learnt of the reload method today and it is very useful
// https://stackoverflow.com/questions/3715047/how-to-reload-a-page-using-javascript
        } else {
            alert('Error voting on post');
        }
    });
}

// AJAX requests are easy to use and prepare when used a couple times. They send a POST request to their
// associated URL (/vote/) with the relavant data, the view processes the data and sends a response
// back to javascript as "response" this is our first promise, we then turn this into JSON object.
// Our second promise then uses the response to update the page

function voteComment(commentId, isUpvote) {
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    fetch('/vote/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            comment_id: commentId,
            is_upvote: isUpvote
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Error voting on comment');
        }
    });
}

$(function() {
    $('#day-night').on('change', function() {
        $('body').toggleClass('night-mode', this.checked);
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const commentActions = document.querySelectorAll('.commentAction');

    commentActions.forEach(button => {
        button.addEventListener('click', function() {
            const target = this.getAttribute('data-bs-target');
            const allCollapses = document.querySelectorAll('.collapse');

            allCollapses.forEach(collapse => {
                if (collapse.id !== target.substring(1)) {
                    collapse.classList.remove('show');
                }
            })
        })
    })
})