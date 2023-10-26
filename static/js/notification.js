const logged_username = JSON.parse(document.getElementById('json-username').textContent);

const notificationSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/user/notification/'
)

notificationSocket.onopen = function (e) {
    console.log("notificationSocket open");
}

notificationSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);

    if (data.room && data.created) {
        const chatMessagesList = document.querySelector('.chat-messages ul');
        const newRoomElement = document.createElement('li');
        newRoomElement.setAttribute('data-room-id', `${data.room}`);

        const chatRoomLink = document.createElement('a');
        chatRoomLink.href = '/chatroom/' + data.room + '/';

        const participantInfo = document.createElement('div');
        participantInfo.className = 'participant-info';

        for (const participant of data.participants) {
            if (participant.username !== logged_username) {
                const participantImage = document.createElement('img');
                participantImage.src = participant.photo;
                participantImage.alt = 'User Image';
                participantImage.className = 'rounded-circle mr-2';
                participantImage.height = 50;
                participantImage.width = 50;

                const participantName = document.createElement('span');
                participantName.className = 'participant-name';
                participantName.textContent = `${participant.first_name} ${participant.last_name}`;

                participantInfo.appendChild(participantImage);
                participantInfo.appendChild(participantName);
            }
        }
        const createBadge = document.createElement('div');
        createBadge.id = `${data.room}_create-badge`;
        participantInfo.appendChild(createBadge);

        chatRoomLink.appendChild(participantInfo);

        newRoomElement.appendChild(chatRoomLink);

        chatMessagesList.insertBefore(newRoomElement, chatMessagesList.firstChild);
    }

    if (data.receiver === logged_username) {
        const chatRoomElement = document.querySelector(`li[data-room-id="${data.room}"]`);

        if (chatRoomElement) {
            // Remove the chat room element from its current position
            chatRoomElement.parentNode.removeChild(chatRoomElement);

            // Insert it at the top of the chat room list
            const chatMessagesList = document.querySelector('.chat-messages ul');
            chatMessagesList.insertBefore(chatRoomElement, chatMessagesList.firstChild);

            const countBadge = document.getElementById(`${data.room}_count-badge`);
            if (countBadge) {
                countBadge.textContent = data.count;
            } else {
                const newCountBadge = document.createElement('div');
                newCountBadge.id = `${data.room}_count-badge`;
                newCountBadge.className = 'count-badge';
                newCountBadge.textContent = data.count;

                const appendBadge = document.getElementById(`${data.room}_create-badge`);
                appendBadge.appendChild(newCountBadge);
            }
        }
    }
}

notificationSocket.onclose = function (e) {
    console.log("notificationSocket closed");
}