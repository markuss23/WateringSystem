let dict = {
    'topic': 'False',
    'payload': 'False'
};
let topic = [];
let payload = [];
let text;
let textPayload;
myStorage = window.localStorage;
let clickable = false;


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
    console.log(JSON.parse(localStorage.getItem('topic')));
    console.log(JSON.parse(localStorage.getItem('payload')));
    let topics = [];
    let payloads = [];
    topics.push(JSON.parse(localStorage.getItem('topic')));
    payloads.push(JSON.parse(localStorage.getItem('payload')));
    console.log($('#typ').text().toString());

    if ($('#typ').text() == "Input") {
        $('#publish').addClass("bg-components-dark");
        $('#publish').removeClass("bg-components, link-brown");
    } else {
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
    }
    for (let i = 0; i < topics[0].length; i++) {
        if ($('#topic').text() === topics[0][i]) {
            if (parseFloat(payloads[0][i])) {
                console.log('tady');
                $('#publish').text(payloads[0][i]);
            } else {
                $('#publish').text(changeState(payloads[0][i]));
            }
        } else {
            $('#publish').text("Nefunkční");
            $('#publish').addClass("bg-components-dark");
            $('#publish').removeClass("bg-components, link-brown");
        }
    }


});
socket.on('mqtt_message', function (data) {
    text = JSON.parse(localStorage.getItem('topic'));
    textPayload = JSON.parse(localStorage.getItem('payload'));
    topic.splice(topic.length - 1, 0, data['topic']);
    removeDuplicates();

    let absent = text.filter(e => !topic.includes(e));
    if (absent.length > 1) {
        for (let i = 0; i < absent.length; i++) {
            topic.splice(topic.length - 1, 0, absent[i]);
        }
    }

    payload[topic.indexOf(data['topic'])] = data['payload'];
    for (let i = 0; i < payload.length; i++) {
        if (!payload[i]) {
            payload[i] = textPayload[i];
        }
    }
    for (let i = 0; i < topic.length; i++) {
        if ($('#topic').text() === topic[i]) {
            if (parseFloat(payload[i])) {
                $('#publish').text(payload[i]);
            } else {
                $('#publish').text(changeState(payload[i]));
            }
        }
    }
})


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

window.onbeforeunload = function (event) {
    localStorage.setItem('topic', JSON.stringify(topic));
    localStorage.setItem('payload', JSON.stringify(payload));
};



