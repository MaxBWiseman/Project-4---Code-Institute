
document.addEventListener('DOMContentLoaded', function() {
/*When all content is loaded, the beloe executes*/
    document.querySelectorAll('.reply-link').forEach(function(link) {
/*Selects all elements with class "reply-link" and iterates with forEach method,
each "link" is one of these elements*/
        link.addEventListener('click', function(event) {
/*For each "link" element, adds an event listener to the click event*/
            event.preventDefault();
/*Prevents the default action of the event (navigating away)*/
            const parentId = this.getAttribute('data-parent-id');
/*Gets the value of the "data-parent-id" attribute of the clicked element*/
            document.getElementById('parent-id').value = parentId;
/*Sets the value of the "parent-id" input field to the value of the "data-parent-id" attribute*/
            document.getElementById('comment-box').focus();
/*Focuses on the comment box*/
        });
    });
});
/* The JavaScript code sets the value of the hidden parent input field to the ID of the comment
 being replied to and focuses on the comment box.*/