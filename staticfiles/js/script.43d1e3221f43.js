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
       <form id="newForm" class="form-insert py-2" method="post">
            <div class="d-flex justify-content-between">
                <h2>You are Replying to: ${author}</h2>
                <div>
                    <button type="button" class="btn btn-danger me-2" onclick="formExit()">Close</button>
                </div>
            </div>
            <input type="hidden" name="csrfmiddlewaretoken" value="${ csrfToken }">
            <select name="parent" class="d-none" id="id_parentt">
                <option value="${id}" selected>${id}</option>
            </select>
            <label for="id_content">Content:</label>
            <textarea name="content" cols="40" rows="5" class="form-control" required id="id_content"></textarea>
            <button type="submit" class="btn btn-primary btn-lg btn-block">Submit</button>
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
});

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
    const editForm = document.getElementById("edit-comment-" + commentId);

    commentContent.style.display = 'none';
    editForm.style.display = 'block';
    // Store the commentId in the hidden input field
    document.getElementById('comment-id').value = commentId;
    // Change the form's submit event handler to update the comment
    const editCommentForm = document.getElementById('edit-comment-form');
    editCommentForm.removeEventListener('submit', defaultFormSubmission);
    editCommentForm.addEventListener('submit', submitEditComment);
}

function submitEditComment(commentId) {
    return function(event) {
        event.preventDefault(); // Prevent the default form submission

        const commentBox = document.getElementById('edit-content-' + commentId);
        const commentText = commentBox.value;
        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

        fetch(`/edit_comment/${commentId}/`, {
// This is the URL to send the request to
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
// headers are used to send additional information to the server,
// like the content type and the CSRF token
            body: JSON.stringify({ content: commentText })
// we use the body property to send the data to the server
// we use JSON.stringify to convert the data to a JSON string
        })
        .then(response => response.json())
// we use the .then method to handle the response from the server
// we use the .json method to convert the response to a JSON object
        .then(data => {
            if (data.success) {
                const commentNew = document.getElementById('edit-content-' + commentId);
                const commentOld = document.getElementById('comment-content-' + commentId);
                commentOld.innerText = commentNew.value;
// Update the original comment box with the new content
// Revert the form's submit event handler back to default behavior
                const editCommentForm = document.getElementById('edit-comment-form');
                editCommentForm.removeEventListener('submit', submitEditComment(commentId));
                editCommentForm.addEventListener('submit', defaultFormSubmission);
                cancelEditComment(commentId);
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