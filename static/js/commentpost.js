const name = JSON.parse(document.getElementById('json-username').textContent);

const commentSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/post/comment/'
);

commentSocket.onopen = function (e) {
    console.log('commentSocket open')
};

commentSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);

    if (data.type === 'send_post_comment') {
        let commentContainer = document.createElement("div");
        commentContainer.setAttribute("data-comment-id", data.comment_id);
        commentContainer.setAttribute("data-post-id", data.post);
        commentContainer.className = "comment mb-2";

        let html = `
            <div class="d-flex align-items-center">
                <img height="30px" width="30px" src="${data.photo}" alt="User Image" class="rounded-circle mr-2">
                <div id="${data.post}_comment" class="flex-grow-1">
                    <p class="mb-0"><strong>${data.username}: </strong>${data.content}</p>
                    <p class="text-muted mb-0"><small>${data.created_at}</small></p>
                </div>
        `;

        if (data.username === name) {
            html += `
                <button class="btn btn-edit-comment" data-comment-id="${data.comment_id}">
                    <b><i class="bi bi-pencil-square">Edit</i></b>
                </button>
                <div class="comment-edit-form" id="comment-edit-form-${data.comment_id}" style="display: none">
                    <form>
                        <label>
                            <input class="form-control input-edit-comment" value="${data.content}" placeholder="Enter your comment" required>
                        </label>
                        <button type="submit" id="${data.post}_${data.comment_id}_edit-button" class="btn btn-sm btn-primary btn-edit">Edit Comment</button>
                        <button type="button" class="btn btn-sm btn-secondary btn-cancel-edit" data-comment-id="${data.comment_id}">Cancel</button>
                    </form>
                </div>
            `;
        }

        if (data.username === name || data.user_post === name) {
            html += `
                <button id="${data.post}_${data.comment_id}_delete-button" class="btn btn-delete-comment btn-delete">
                    <b><i class="bi bi-pencil-square">X</i></b>
                </button>
            `;
        }

        html += `</div>`;
        commentContainer.innerHTML = html;

        document.getElementById(`${data.post}_comments`).appendChild(commentContainer);

        let zeroCommentsMessage = document.getElementById(`${data.post}_no_comments`);
        if (zeroCommentsMessage) {
            zeroCommentsMessage.style.display = "none";
        }
    }

    if (data.type === 'send_delete_post_comment') {
        let commentContainerToDelete = document.querySelector(`[data-comment-id="${data.comment_id}"]`);
        commentContainerToDelete.remove();

        let comments = document.querySelectorAll(`[data-post-id="${data.post}"]`);
        let zeroCommentsMessage = document.createElement("div");
        let existingZeroCommentsMessage = document.getElementById(`${data.post}_no_comments`);

        if (comments.length === 0) {
            if (existingZeroCommentsMessage) {
                existingZeroCommentsMessage.remove();
            }
            zeroCommentsMessage.id = `${data.post}_no_comments`;
            zeroCommentsMessage.innerHTML = '<p class="mb-0">0 Comments</p>';
            document.getElementById(`${data.post}_comments`).appendChild(zeroCommentsMessage);
        }
    }

    if (data.type === 'send_edit_post_comment') {
        const commentElement = document.querySelector(`[data-comment-id="${data.comment_id}"]`);
        const commentContentElement = commentElement.querySelector('.flex-grow-1 p');
        commentContentElement.innerHTML = `<strong>${data.username}: </strong>${data.content}`;

        if (EditComment[data.comment_id]) {
            const editButton = document.querySelector(`.btn-edit-comment[data-comment-id="${data.comment_id}"]`);
            editButton.click();
        }
    }
}

commentSocket.onclose = function (e) {
    console.log('commentSocket closed');
};

const EditComment = {};

document.addEventListener("DOMContentLoaded", function () {
    // console.log("DOMContentLoaded event fired");
    document.body.addEventListener("click", function (event) {

        // Handle Create Comments
        const commentButton = event.target.closest('.btn-comment');
        if (commentButton) {
            event.preventDefault();
            const commentInput = commentButton.closest('form').querySelector('.input-comment');
            const comment = commentInput.value.trim();
            const postId = commentButton.id.replace('_submit-comment', '');
            if (comment !== '') {
                commentSocket.send(JSON.stringify({
                    'type': 'create_comment',
                    'content': comment,
                    'username': name,
                    'post': postId,
                }));
                commentInput.value = '';
            }
        }

        // Handle Delete Comments
        const deleteButton = event.target.closest('.btn-delete');
        if (deleteButton) {
            event.preventDefault();
            const id = deleteButton.id.split('_');
            const postId = id[0];
            const commentId = id[1];
            commentSocket.send(JSON.stringify({
                'type': 'delete_comment',
                'username': name,
                'post': postId,
                'comment_id': commentId,
            }));
        }

        // Handle Edit Comments
        const editButton = event.target.closest('.btn-edit');
        if (editButton) {
            event.preventDefault();
            const commentInput = editButton.closest('form').querySelector('.input-edit-comment');
            const comment = commentInput.value.trim();
            const id = editButton.id.split('_');
            const postId = id[0];
            const commentId = id[1];
            if (comment !== '') {
                commentSocket.send(JSON.stringify({
                    'type': 'edit_comment',
                    'content': comment,
                    'username': name,
                    'post': postId,
                    'comment_id': commentId,
                }));
            }
        }

        // Handle the show/hide Edit Comments
        const editOldButton = event.target.closest(".btn-edit-comment");
        if (editOldButton) {
            const commentId = editOldButton.getAttribute("data-comment-id");
            const editForm = document.getElementById(`comment-edit-form-${commentId}`);

            if (EditComment[commentId]) {
                editForm.style.display = "none";
                EditComment[commentId] = false;
                editOldButton.style.display = "block";
            } else {
                editForm.style.display = "block";
                EditComment[commentId] = true;
                editOldButton.style.display = "none";
            }
        }

        // Handle the show/hide Cancel Comments
        if (event.target.classList.contains("btn-cancel-edit")) {
            const commentId = event.target.getAttribute("data-comment-id");
            const editForm = document.getElementById(`comment-edit-form-${commentId}`);
            editForm.style.display = "none";
            EditComment[commentId] = false;
            const editOldButton = document.querySelector(`.btn-edit-comment[data-comment-id="${commentId}"]`);
            editOldButton.style.display = "block";
        }
    });
});