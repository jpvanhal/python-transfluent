from io import BytesIO, StringIO

from flexmock import flexmock
import pytest
import requests


def make_transfluent(*args, **kwargs):
    from transfluent import Transfluent
    return Transfluent(*args, **kwargs)


def make_transfluent_error(*args, **kwargs):
    from transfluent import TransfluentError
    return TransfluentError(*args, **kwargs)


def make_error_response():
    response = requests.Response()
    response.status_code = 400
    response.raw = BytesIO(
        '{"status":"ERROR","error":{"type":"EBackendParameterInvalid","mes'
        'sage":"Name is required!"},"response":"Unfortunately an error occ'
        'ured. You might want to try again. If problem persists, please re'
        'port this as a bug. We are sorry for inconvenience."}'
    )
    return response


class TestTransfluent(object):

    def test_constructor_without_parameters_sets_token_to_none(self):
        client = make_transfluent()
        assert client.token is None

    def test_constructor_sets_token(self):
        client = make_transfluent(token='foo')
        assert client.token == 'foo'

    def test_constructor_sets_transfluent_url(self):
        client = make_transfluent()
        assert client._transfluent_url == 'https://transfluent.com/v2/'

    def test_request_on_successful_json_response(self):
        response = requests.Response()
        response.status_code = 200
        response.raw = BytesIO('{"status":"OK","response":"Hello World"}')
        (
            flexmock(requests)
            .should_receive('request')
            .with_args(
                'GET',
                'https://transfluent.com/v2/hello/World/',
                params=None
            )
            .and_return(response)
            .once()
        )
        client = make_transfluent()
        response = client._request('GET', 'hello/World/')
        assert response == u'Hello World'

    def test_request_on_successful_non_json_response(self):
        response = requests.Response()
        response.status_code = 200
        response.raw = BytesIO('some content')
        (
            flexmock(requests)
            .should_receive('request')
            .with_args(
                'GET',
                'https://transfluent.com/v2/hello/World/',
                params=None
            )
            .and_return(response)
            .once()
        )
        client = make_transfluent()
        response = client._request('GET', 'hello/World/')
        assert response == u'some content'

    def test_request_on_error_raises_exception(self):
        from transfluent import TransfluentError
        response = make_error_response()
        (
            flexmock(requests)
            .should_receive('request')
            .with_args(
                'GET',
                'https://transfluent.com/v2/hello/',
                params=None
            )
            .and_return(response)
            .once()
        )
        client = make_transfluent()
        with pytest.raises(TransfluentError) as excinfo:
            response = client._request('GET', 'hello/')
        exception = excinfo.value
        assert exception.type == 'EBackendParameterInvalid'
        assert exception.message == 'Name is required!'

    def test_authed_request_without_parameters(self):
        client = make_transfluent(token='foo')
        fake_rv = flexmock()
        (
            flexmock(client)
            .should_receive('_request')
            .with_args('GET', 'customer/name/', {'token': 'foo'})
            .and_return(fake_rv)
            .once()
        )
        rv = client._authed_request('GET', 'customer/name/')
        assert rv is fake_rv

    def test_authed_request_with_parameters(self):
        client = make_transfluent(token='foo')
        fake_rv = flexmock()
        (
            flexmock(client)
            .should_receive('_request')
            .with_args(
                'POST',
                'customer/name/',
                {'token': 'foo', 'name': 'John'}
            )
            .and_return(fake_rv)
            .once()
        )
        rv = client._authed_request('POST', 'customer/name/', {'name': 'John'})
        assert rv is fake_rv

    def test_authenticate_sets_token(self):
        client = make_transfluent()
        (
            flexmock(client)
            .should_receive('_request')
            .with_args(
                'GET',
                'authenticate',
                {'email': 'john@example.com', 'password': 'test'}
            )
            .and_return({'token': 'foo'})
            .once()
        )
        client.authenticate(email='john@example.com', password='test')
        assert client.token == 'foo'

    def test_languages(self):
        client = make_transfluent()
        fake_rv = flexmock()
        (
            flexmock(client)
            .should_receive('_request')
            .with_args('GET', 'languages')
            .and_return(fake_rv)
            .once()
        )
        assert client.languages is fake_rv

    def test_retrieving_customer_name(self):
        client = make_transfluent()
        fake_rv = flexmock()
        (
            flexmock(client)
            .should_receive('_authed_request')
            .with_args('GET', 'customer/name')
            .and_return(fake_rv)
            .once()
        )
        assert client.customer_name is fake_rv

    def test_setting_customer_name(self):
        client = make_transfluent()
        (
            flexmock(client)
            .should_receive('_authed_request')
            .with_args('POST', 'customer/name', {'name': 'John Doe'})
            .once()
        )
        client.customer_name = 'John Doe'

    def test_retrieving_customer_email(self):
        client = make_transfluent()
        fake_rv = flexmock()
        (
            flexmock(client)
            .should_receive('_authed_request')
            .with_args('GET', 'customer/email')
            .and_return(fake_rv)
            .once()
        )
        assert client.customer_email is fake_rv

    def test_setting_customer_email(self):
        client = make_transfluent()
        (
            flexmock(client)
            .should_receive('_authed_request')
            .with_args(
                'POST',
                'customer/email',
                {'email': 'john.doe@example.com'}
            )
            .once()
        )
        client.customer_email = 'john.doe@example.com'

    def test_file_status(self):
        client = make_transfluent()
        fake_rv = flexmock()
        (
            flexmock(client)
            .should_receive('_authed_request')
            .with_args(
                'GET',
                'file/status',
                {'identifier': 'my-project/messages', 'language': 11}
            )
            .and_return(fake_rv)
            .once()
        )
        rv = client.file_status('my-project/messages', 11)
        assert rv is fake_rv

    def test_is_file_complete_when_file_has_been_translated(self):
        client = make_transfluent()
        (
            flexmock(client)
            .should_receive('file_status')
            .with_args('my-project/messages', 11)
            .and_return({'progress': '100%'})
            .once()
        )
        assert client.is_file_complete('my-project/messages', 11) is True

    def test_is_file_complete_when_file_has_not_been_translated(self):
        client = make_transfluent()
        (
            flexmock(client)
            .should_receive('file_status')
            .with_args('my-project/messages', 11)
            .and_return({'progress': '37.55%'})
            .once()
        )
        assert client.is_file_complete('my-project/messages', 11) is False

    def test_file_save_with_file_object(self):
        client = make_transfluent()
        fake_rv = flexmock()
        (
            flexmock(client)
            .should_receive('_authed_request')
            .with_args(
                'POST',
                'file/save',
                {
                    'identifier': 'my-project/messages',
                    'language': 1,
                    'format': 'UTF-8',
                    'content': 'ZmlsZSBjb250ZW50cw==',
                    'type': 'po-file',
                    'save_only_data': 0
                }
            )
            .and_return(fake_rv)
            .once()
        )
        rv = client.file_save(
            'my-project/messages',
            1,
            StringIO(u"file contents"),
            'po-file'
        )
        assert rv is fake_rv

    def test_file_save_with_file_contents_as_string(self):
        client = make_transfluent()
        fake_rv = flexmock()
        (
            flexmock(client)
            .should_receive('_authed_request')
            .with_args(
                'POST',
                'file/save',
                {
                    'identifier': 'my-project/messages',
                    'language': 1,
                    'format': 'UTF-8',
                    'content': 'ZmlsZSBjb250ZW50cw==',
                    'type': 'po-file',
                    'save_only_data': 0
                }
            )
            .and_return(fake_rv)
            .once()
        )
        rv = client.file_save(
            'my-project/messages',
            1,
            "file contents",
            'po-file'
        )
        assert rv is fake_rv

    def file_translate(self):
        client = make_transfluent()
        fake_rv = flexmock()
        (
            flexmock(client)
            .should_receive('_authed_request')
            .with_args(
                'POST',
                'file/translate',
                {
                    'identifier': 'my-project/messages',
                    'language': 1,
                    'target_languages[]': [11, 14],
                    'comment': '',
                    'callback_url': '',
                    'level': 3
                }
            )
            .and_return(fake_rv)
            .once()
        )
        rv = client.file_translate('my-project/messages', 1, [11, 14])
        assert rv is fake_rv

    def test_file_read(self):
        client = make_transfluent()
        fake_rv = flexmock()
        (
            flexmock(client)
            .should_receive('_authed_request')
            .with_args(
                'GET',
                'file/read',
                {
                    'identifier': 'my-project/messages',
                    'language': 11,
                }
            )
            .and_return(fake_rv)
            .once()
        )
        rv = client.file_read('my-project/messages', 11)
        assert rv is fake_rv


class TestTransfluentError(object):
    def test_constructor_sets_response(self):
        response = make_error_response()
        exception = make_transfluent_error(response)
        assert exception.response is response

    def test_constructor_sets_type_from_response(self):
        response = make_error_response()
        exception = make_transfluent_error(response)
        assert exception.type == 'EBackendParameterInvalid'

    def test_constructor_sets_message_from_response(self):
        response = make_error_response()
        exception = make_transfluent_error(response)
        assert exception.message == 'Name is required!'

    def test_repr(self):
        response = make_error_response()
        exception = make_transfluent_error(response)
        assert (
            repr(exception) ==
            '<TransfluentError [EBackendParameterInvalid]>'
        )

    def test_str(self):
        response = make_error_response()
        exception = make_transfluent_error(response)
        assert str(exception) == 'Name is required!'
