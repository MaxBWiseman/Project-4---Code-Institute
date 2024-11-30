// __tests__/script.test.js
const $ = require('jquery');
global.$ = $;

function formExit() {
    $("#newForm").remove();
}

function grabOne(id) {
    if ($("#newForm").length) {
        $("#newForm").remove();
    }

    var author = $(`#comment-${id} .comment-author`).text().replace('By ', '');
    var csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    var formHtml = `
    <form id="newForm" class="form-insert py-2" method="post" enctype='multipart/form-data'>
         <div class="d-flex justify-content-between">
             <h2>You are Replying to: ${author}</h2>
             <div>
                 <button type="button" class="me-2" style="width:fit-content!important;" onclick="formExit()">Close</button>
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

    $(`#comment-${id}`).after(formHtml);
}

describe('formExit', () => {
    test('should remove the form with id "newForm"', () => {
        document.body.innerHTML = '<form id="newForm"></form>';
        formExit();
        expect(document.getElementById('newForm')).toBeNull();
    });
});

describe('grabOne', () => {
    beforeEach(() => {
        document.body.innerHTML = `
            <div id="comment-1" class="comment">
                <span class="comment-author">By Author</span>
            </div>
            <input type="hidden" name="csrfmiddlewaretoken" value="test-csrf-token">
        `;
    });

    test('should insert reply form after the comment', () => {
        grabOne(1);
        const form = document.getElementById('newForm');
        expect(form).not.toBeNull();
        expect(form.querySelector('h2').textContent).toBe('You are Replying to: Author');
        expect(form.querySelector('input[name="csrfmiddlewaretoken"]').value).toBe('test-csrf-token');
    });

    test('should remove existing form before inserting a new one', () => {
        document.body.innerHTML += '<form id="newForm"></form>';
        grabOne(1);
        const forms = document.querySelectorAll('#newForm');
        expect(forms.length).toBe(1);
    });
});
