$(document).ready(function () {
    let topic = $("#topic").text();
    let qos = 1;
    let data = '{"topic": "' + topic + '", "qos": ' + qos + '}';
    console.log(topic);
    if (topic) {
        console.log('jsem tady');
        socket.emit('subscribe', data = data);
    } else {
        console.log('nejsem tady');
    }
});
socket.on('mqtt_message', function (data) {
    if (data['payload'] === 'on') {
        $('#publish').text('off');
        $('#publish').val('off');
    } else {
        $('#publish').text('on');
        $('#publish').val('on');
    }
    socket.emit('unsubscribe_all');
})

$('#publish').click(function (event) {
    let topic = $('#topic').text();
    if (getShelly(topic) === true) {
        topic = topic + '/command';
    }
    let message = $('#publish').text();
    let qos = 2;
    let data = '{"topic": "' + topic + '", "message": "' + message + '", "qos": ' + qos + '}';
    if ($('#publish').text() === 'on') {
        $('#publish').text('off');
        $('#publish').val('off');
    } else {
        $('#publish').text('on');
        $('#publish').val('on');
    }
    socket.emit('publish', data = data);
});

function changeState(state) {
    if (state === 'on') {
        return 'off';
    } else {
        return 'on';
    }
}

function getShelly(topic) {
    let topics = topic;
    let slice = topics.slice(-7, -2);
    if (slice === 'relay') ;
    return true;
}