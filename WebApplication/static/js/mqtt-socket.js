let dict = {};
let topic = [];
let payload = [];
$(document).ready(function () {
    let json = JSON.parse(sessionStorage.getItem('devices'))
    let topics = [];
    let payloads = []
    topics.push(json['topic']);
    payloads.push(json['payload']);
    for (let i = 0; i < topics[0].length; i++) {
        if ($('#topic').text() === topics[0][i]) {
            if (parseFloat(payloads[0][i])){
                console.log('tady');
                $('#publish').text(payloads[0][i]);
            }
            else{
                $('#publish').text(changeState(payloads[0][i]));
            }
        }
    }


});
socket.on('mqtt_message', function (data) {
    topic.push(data['topic'])
    payload.push(data['payload'])
    dict = {
        'topic': topic,
        'payload': payload
    }

    for (let i = 0; i < topic[0].length; i++) {
        if ($('#topic').text() === topic[0][i]) {
            if (parseFloat(payload[0][i])){
                console.log('tady');
                $('#publish').text(payload[0][i]);
            }
            else{
                $('#publish').text(changeState(payload[0][i]));
            }
        }

    }
    console.log(payload);

    sessionStorage.setItem('devices', JSON.stringify(dict))

})

$('#publish').click(function (event) {
    topic.pop();
    payload.pop();

    let topics = $('#topic').text();
    if (getShelly(topics) === true) {
        topics = topics + '/command';
    }
    let message = $('#publish').text();
    let qos = 2;
    let data = '{"topic": "' + topics + '", "message": "' + message + '", "qos": ' + qos + '}';
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

/*
let topic = $("#topic").text();
let qos = 1;
let data = '{"topic": "' + topic + '", "qos": ' + qos + '}';
console.log(topic);
if (topic) {
    console.log('jsem tady');
    socket.emit('subscribe', data = data);
} else {
    console.log('nejsem tady');
}*/