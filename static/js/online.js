const logged_user = JSON.parse(document.getElementById('json-username').textContent);
const last_logoutElement = document.getElementById('json-last_logout');
const last_seen = last_logoutElement ? JSON.parse(last_logoutElement.textContent) : null;


const onlineSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/user/online/'
)

onlineSocket.onopen = function (e) {
    console.log("onlineSocket open");
    onlineSocket.send(JSON.stringify({
        'type': 'send_status',
        'username': logged_user,
        'c_type': 'open'
    }))
}
window.addEventListener("beforeunload", function (e) {
    onlineSocket.send(JSON.stringify({
        'type': 'send_status',
        'username': logged_user,
        'c_type': 'close'
    }))
})

onlineSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    // console.log(data)
    if (data.username !== logged_user) {
        let userStatus = document.getElementById(`${data.username}_status`);
        if (userStatus) {
            let status = '';
            if (data.is_online === true) {
                status = 'online';
            } else {
                status = `Last Seen ${last_seen}`;
            }
            userStatus.textContent = status;
        }
    }
}

onlineSocket.onclose = function (e) {
    console.log("onlineSocket closed");
}