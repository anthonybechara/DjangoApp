const chatRoomName = JSON.parse(document.getElementById('json-chatroom-name').textContent)
const username = JSON.parse(document.getElementById('json-username').textContent);
const firstname = JSON.parse(document.getElementById('json-first-name').textContent);
const lastname = JSON.parse(document.getElementById('json-last-name').textContent);
const participants_count = JSON.parse(document.getElementById('json-participants_count').textContent);

const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/'
    + chatRoomName
    + '/'
);

chatSocket.onopen = function (e) {
    console.log('chatSocket open')
    scroll()
};

chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);

    if (data.type === 'chat_message') {
        if (data.message && data.room === chatRoomName) {
            const messageClass = data.username === username ? 'right' : 'left';
            let messageDisplay = '';

            if (data.participants > 2 && data.username !== username) {
                messageDisplay = `<b>${data.first_name} ${data.last_name}: </b>${data.message}`;
            } else {
                messageDisplay = data.message;
            }

            const html = `
                <div class="message ${messageClass}">
                    <span class="message-text ${messageClass}">${messageDisplay}</span>
                    <div class="message-timestamp">${data.timestamp}</div>
                </div>
            `;
            document.getElementById('chat-messages').innerHTML += html;

            chatSocket.send(JSON.stringify({
                'type': 'mark_as_read',
                'username': username,
                'room': chatRoomName,
                'is_seen': true,
            }));
        }
    } else if (data.type === 'writing_active' && data.username !== username && data.room === chatRoomName) {
        const remove = document.querySelector('.remove');

        if (remove) {
            remove.remove();
        }

        if (data.message) {
            const html = `<div class="remove"><i>${data.first_name} ${data.last_name} is ${data.message}</i></div>`;
            document.getElementById('chat-messages').innerHTML += html;
        }
    } else if (data.type === 'writing_inactive') {
        const remove = document.querySelector('.remove');
        if (remove) {
            remove.remove();
        }
    }
    scroll();
};

chatSocket.onclose = function (e) {
    console.log('chatSocket closed');
};

let typingTimer;
document.getElementById('message-input').onkeydown = function (e) {
    chatSocket.send(JSON.stringify({
        'type': 'typing',
        'message': 'Typing...',
        'username': username,
        'room': chatRoomName,
        'first_name': firstname,
        'last_name': lastname,
    }));
};

document.getElementById('message-input').onkeyup = function (e) {
    clearTimeout(typingTimer);
    typingTimer = setTimeout(function () {
        chatSocket.send(JSON.stringify({
            'type': 'not-typing',
            'message': '',
            'username': username,
            'room': chatRoomName,
        }));
    }, 300);
};

document.getElementById('send-button').onclick = function (e) {
    e.preventDefault();
    const messageInput = document.getElementById('message-input');
    const message = messageInput.value.trim();
    if (message !== '') {
        chatSocket.send(JSON.stringify({
            'type': 'message',
            'message': message,
            'username': username,
            'room': chatRoomName,
            'first_name': firstname,
            'last_name': lastname,
            'participants': participants_count,
            'receivers': receivers,
        }));
        messageInput.value = '';
    }
};

function scroll() {
    const chatMessages = document.getElementById('chat-messages');
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
