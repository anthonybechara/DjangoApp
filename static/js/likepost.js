const user = JSON.parse(document.getElementById('json-username').textContent);

const likeSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/post/like/'
);

likeSocket.onopen = function (e) {
    console.log("likeSocket open");
};

function getRandomItem(array) {
    return array[Math.floor(Math.random() * array.length)];
}

likeSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);

    let likeUserW = data.likers.filter(function (x) {
        return x !== user;
    });
    let randomUserLike = getRandomItem(likeUserW);

    if (data.username === user) {
        const likeButton = document.getElementById(`${data.post}_like-button`);

        if (data.user_liked === true) {
            likeButton.innerHTML = 'Liked';
            likeButton.classList.remove('btn-outline-primary');
            likeButton.classList.add('btn-primary');
        } else {
            likeButton.innerHTML = 'Like';
            likeButton.classList.remove('btn-primary');
            likeButton.classList.add('btn-outline-primary');
        }
    }

    let likeMessage = "";
    if (data.like === 0) {
        likeMessage = "No likes yet";
    } else if (data.like === 1) {
        likeMessage = `Liked by ${data.likers}`;
    } else if (data.like === 2) {
        likeMessage = `Liked by ${randomUserLike} and 1 other`;
    } else {
        likeMessage = `Liked by ${randomUserLike} and ${data.like - 1} others`;
    }

    const likesInfoElement = document.getElementById(`${data.post}_likes-info`);
    likesInfoElement.innerHTML = `<strong>Likes:</strong> ${likeMessage}`;
}


likeSocket.onclose = function (e) {
    console.log("likeSocket closed");
};

// Add a click event listener to each like button
const likeButtons = document.querySelectorAll('.btn-like');
likeButtons.forEach(function (button) {
    button.addEventListener('click', function (e) {
        e.preventDefault();
        const postId = button.id.replace('_like-button', '');
        likeSocket.send(JSON.stringify({
            'username': user,
            'post': postId,
        }));
    });
});
