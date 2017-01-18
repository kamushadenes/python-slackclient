from slackclient._slackrequest import SlackRequest
import json
import os

def test_http_headers(mocker):
    requests = mocker.patch('slackclient._slackrequest.requests')
    request = SlackRequest()

    request.append_user_agent("fooagent1","0.1")
    request.append_user_agent("baragent/2","0.2")

    request.do('xoxb-123', 'chat.postMessage', {'text': 'test', 'channel': '#general'})

    args, kwargs = requests.post.call_args
    assert None != kwargs['headers']['user-agent']

    # Verify user-agent includes both default and custom agent info
    assert "slackclient" in kwargs['headers']['user-agent']
    assert "fooagent1" in kwargs['headers']['user-agent']

    # verify escaping of slashes in custom agent name
    assert "baragent:2" in kwargs['headers']['user-agent']

def test_post_file(mocker):
    requests = mocker.patch('slackclient._slackrequest.requests')
    request = SlackRequest()

    response = request.do('xoxb-123',
        'files.upload',
        {'file': open(os.path.join('.', 'tests', 'data', 'slack_logo.png'), 'rb'),
            'filename': 'slack_logo.png'})

    assert requests.post.call_count == 1
    args, kwargs = requests.post.call_args
    assert 'https://slack.com/api/files.upload' == args[0]
    assert {'filename': 'slack_logo.png',
            'token': 'xoxb-123'} == kwargs['data']
    assert None != kwargs['files']

def test_get_file(mocker):
    requests = mocker.patch('slackclient._slackrequest.requests')
    request = SlackRequest()

    request.do('xoxb-123', 'files.info', {'file': 'myFavoriteFileID'})

    assert requests.post.call_count == 1
    args, kwargs = requests.post.call_args
    assert 'https://slack.com/api/files.info' == args[0]
    assert {'file': "myFavoriteFileID",
            'token': 'xoxb-123'} == kwargs['data']
    assert None == kwargs['files']

def test_post_attachements(mocker):
    requests = mocker.patch('slackclient._slackrequest.requests')
    request = SlackRequest()

    request.do('xoxb-123',
                    'chat.postMessage',
                    {'attachments': [{'title': 'hello'}]})

    assert requests.post.call_count == 1
    args, kwargs = requests.post.call_args
    assert 'https://slack.com/api/chat.postMessage' == args[0]
    assert {'attachments': json.dumps([{'title': 'hello'}]),
            'token': 'xoxb-123'} == kwargs['data']
    assert None == kwargs['files']
