document.addEventListener('DOMContentLoaded', function() {
    console.log('Script loaded!');
    document.querySelectorAll('.reply-link').forEach(function(link) {
/*Iterates through items with the class "reply-link" using the forEach method, every "link"
will be one of the parent comments in the given post */
        console.log('Link found!');
        link.addEventListener('click', function(event) {
/*Click event lisitiener */
            console.log('Link clicked!');
            event.preventDefault();
/*Prevent the default action of the link (taking user somewhere else) */
            const parentId = this.getAttribute('data-parent-id');
/*Gets the value of the data-parent-id attribute of the clicked link */
            console.log('Parent ID:', parentId);
            const parentInput = document.getElementById('id_parent');
/*This hidden input field we are grabbing is used to store the ID of the parent comment to which
the reply is being made */
            const replyFormContainer = document.getElementById('reply-form-container');
/*This is the container that holds the reply form */
            if (parentInput && replyFormContainer) {
/*If both the parent input and the reply form container are found */
                parentInput.value = parentId;
/*Set the value of the parent input to the ID of the parent comment */
                replyFormContainer.style.display = 'block';
/*Display the reply form container */
                replyFormContainer.scrollIntoView({ behavior: 'smooth' });
/*Scroll the reply form container into view */
                console.log('Parent ID set and comment box focused');
            } else {
                console.error('Parent input or comment box not found');
            }
        });
    });
     // Prevent multiple form submissions
     const form = document.getElementById('comment-form');
/*Get the comment form */
     form.addEventListener('submit', function(event) {
/*Add an event listener for the form submission */
         const submitButton = document.getElementById('submit-button');
/*Get the submit button */
         if (submitButton.disabled) {
/*If the submit button is disabled */
             event.preventDefault();
/*Prevent the form submission */
             return;
         }
         submitButton.disabled = true;
/*Disable the submit button */
     });
      // Prevent multiple form submissions for reply comments
    const replyForm = document.getElementById('reply-form');
    replyForm.addEventListener('submit', function(event) {
        const replySubmitButton = document.getElementById('reply-submit-button');
        if (replySubmitButton.disabled) {
            event.preventDefault();
            return;
        }
        replySubmitButton.disabled = true;
    });
});