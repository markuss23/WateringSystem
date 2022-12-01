let dict = {};
let topic = [];
let payload = [];
myStorage = window.localStorage;

function removeDuplicates() {
    let unique = [];
    topic.forEach(element => {
        if (!unique.includes(element)) {
            unique.push(element);
        }
    });
    topic = unique;
}



$(document).ready(function () {
    console.log(JSON.parse(myStorage.getItem('devices')));
    let json = JSON.parse(myStorage.getItem('devices'));
    let topics = [];
    let payloads = [];
    topics.push(json['topic']);
    payloads.push(json['payload']);
    for (let i = 0; i < topics[0].length; i++) {
        if ($('#topic').text() === topics[0][i]) {
            if (parseFloat(payloads[0][i])) {
                console.log('tady');
                $('#publish').text(payloads[0][i]);
            } else {
                $('#publish').text(changeState(payloads[0][i]));
            }
        }
    }


});
socket.on('mqtt_message', function (data) {
    let indexTopic = 0;
    topic.push(data['topic'])
    dict = {
        'topic': topic,
        'payload': payload
    }
    removeDuplicates();
    payload[topic.indexOf(data['topic'])] = data['payload'];


    for (let i = 0; i < topic.length; i++) {
        if ($('#topic').text() === topic[i]) {
            if (parseFloat(payload[i])) {
                $('#publish').text(payload[i]);
            } else {
                $('#publish').text(changeState(payload[i]));
            }
        }
    }


    dict['topic'] = topic;
    dict['payload'] = payload;
    myStorage.setItem('devices', JSON.stringify(dict))

    //console.log(sessionStorage.getItem('devices'));
})

$('#publish').click(function (event) {

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
window.onbeforeunload = function (e) {
    console.log(e);
    myStorage.setItem('devices', JSON.stringify(dict));
    console.log("tu jsem");
};*/