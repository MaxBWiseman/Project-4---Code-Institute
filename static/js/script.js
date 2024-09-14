document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.reply-link').forEach(function(link) {
        link.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent the default action of the link
            console.log('Reply link clicked');
            
            const parentId = this.getAttribute('data-parent-id'); // Get the parent ID from the clicked link
            console.log('Parent ID:', parentId);
            
            const parentInput = document.getElementById('id_parent'); // Get the hidden input field
            console.log('Parent input field:', parentInput);
            
            const replyFormContainer = document.getElementById('reply-form-container'); // Get the reply form container
            console.log('Reply form container:', replyFormContainer);
            
            if (parentInput && replyFormContainer) {
                parentInput.value = parentId; // Set the value of the hidden input field to the parent ID
                console.log('Set parent input value to:', parentId);
                
                replyFormContainer.style.display = 'block'; // Display the reply form
                console.log('Displayed reply form container');
                
                replyFormContainer.scrollIntoView({ behavior: 'smooth' }); // Scroll to the reply form
                console.log('Scrolled to reply form container');
            } else {
                console.error('Parent input or reply form container not found');
            }
        });
    });
});