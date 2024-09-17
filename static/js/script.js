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

    var formHtml = `
       <form id="newForm" class="form-insert py-2" method="post">
            <div class="d-flex justify-content-between">
                <h2>You are Replying to: ${author}</h2>
                <div>
                    <button type="button" class="btn btn-outline-secondary" onclick="formExit()">Close</button>
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

function confirmDelete(commentId) {
    const modal = document.getElementById('deleteModal');
    const confirmBtn = document.getElementById('confirmDeleteBtn');
    modal.style.display = 'block';
    confirmBtn.onclick = function() {
    deleteComment(commentId);
};
}

function editComment(commentId) {
    const commentBox = document.getElementById('id_content');
    const commentContent = document.getElementById('edit-content-' + commentId);
    const commentText = commentContent.value;
    commentBox.value = commentText;
    commentBox.focus();
    commentBox.scrollIntoView({ behaviour: 'smotth', block: 'center' });


}

function closeModal() {
    const modal = document.getElementById('deleteModal');
    modal.style.display = 'none';
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
        } else {
            alert('Error deleting comment');
        }
    });
}