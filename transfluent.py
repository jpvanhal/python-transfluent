# -*- coding: utf-8 -*-
"""
    transfluent
    ~~~~~~~~~~~

    :copyright: (c) 2013 by Janne Vanhala.
    :license: BSD, see LICENSE for more details.
"""
import base64

import requests

__version__ = '0.2.0'

TRANSFLUENT_URL = 'https://transfluent.com/v2/'


class Transfluent(object):
    def __init__(self, token=None):
        self.token = token
        self._transfluent_url = TRANSFLUENT_URL

    def _request(self, method, path, data=None):
        url = self._transfluent_url + path
        kwargs = {}
        if method.upper() == 'GET':
            kwargs['params'] = data
        elif method.upper() == 'POST':
            kwargs['data'] = data
        else:
            raise ValueError('Unsupported request method: {0}'.format(method))
        response = requests.request(method, url, **kwargs)
        if response.status_code != 200:
            raise TransfluentError(response)
        try:
            data = response.json()
        except ValueError:
            return response.content
        else:
            return data['response']

    def _authed_request(self, method, path, data=None):
        data = data or {}
        data['token'] = self.token
        return self._request(method, path, data)

    def authenticate(self, email, password):
        data = {'email': email, 'password': password}
        response = self._request('GET', 'authenticate', data)
        self.token = response['token']

    @property
    def customer_name(self):
        return self._authed_request('GET', 'customer/name')

    @customer_name.setter
    def customer_name(self, name):
        self._authed_request('POST', 'customer/name', {'name': name})

    @property
    def customer_email(self):
        return self._authed_request('GET', 'customer/email')

    @customer_email.setter
    def customer_email(self, email):
        self._authed_request('POST', 'customer/email', {'email': email})

    @property
    def languages(self):
        return self._request('GET', 'languages')

    def texts_save(self, group_id, language, texts,
                   invalidate_translations=True):
        """
        Save texts to the system.

        :param group_id:
            Group id for texts (alphanumeric string, recommended max
            length 32 characters). All text ids in group are visible
            only in the group (e.g. text ids won't collide between
            groups).

        :type group_id: str

        :param language:
            The human language of the texts. E.g. 1 = English (GB),
            11 = Finnish. Please refer to :attr:`languages` for full
            list of language ids.

        :type language: int

        :param texts:
            A dict of text keys and content.

        :type texts: dict

        :param invalidate_translations:
            Optional. A boolean value which controls if translations are
            trashed or not. E.g. if you make a spelling error correction
            to the original text, you probably don't want to trash the
            translations and re-translate the text. Also if you save
            previously made translation to the system using this
            method, it's really important to set
            `invalidate_translations` off!

            Defaults to `True`.

            .. warning::
            Affects ALL texts set on the same request. If you need to
            invalidate some and keep others, you have to perform two
            requests.

        :type invalidate_translations: bool
        """
        data = {
            'group_id': group_id,
            'language': language,
            'invalidate_translations': 1 if invalidate_translations else 0,
        }
        for key, content in texts.iteritems():
            data['texts[{0}]'.format(key)] = content
        return self._authed_request('POST', 'texts', data)

    def texts_read(self, group_id, language, limit=100, offset=0):
        """
        Read texts from the system.

        :param group_id:
            Group id for texts (alphanumeric string, recommended max
            length 32 characters). All text ids in group are visible
            only in the group (e.g. text ids won't collide between
            groups).

        :type group_id: str

        :param language:
            The human language of the texts. E.g. 1 = English (GB),
            11 = Finnish. Please refer to :attr:`languages` for full
            list of language ids.

        :type language: int

        :type limit: int

        :type offset: int
        """
        data = {
            'group_id': group_id,
            'language': language,
            'limit': limit,
            'offset': offset,
        }
        return self._authed_request('GET', 'texts', data)

    def texts_translate(self, group_id, language, target_languages, texts,
                        **kwargs):
        """
        Order translations for new and changed texts.

        :param group_id:
            Group id for texts (alphanumeric string, recommended max
            length 32 characters). All text ids in group are visible
            only in the group (e.g. text ids won't collide between
            groups).

        :type group_id: str

        :param language:
            The human language the source text is written in.
            E.g. 1 = English (GB), 11 = Finnish. Please refer to
            :attr:`languages` for full list of language ids.

        :type language: int

        :param target_languages:
            A list of target languages to translate texts into. Please
            refer to :attr:`languages` for full list of language ids.

        :type target_languages: list

        :param texts:
            A list of text ids of texts to translate.

        :type texts: list

        :param callback_url:
            Optional. A GET request will be performed on this URL when
            the translation is ready.

        :type callback_url: str

        :param level:
            Optional. The level of tranlators. The supported values are:

            - `1`. A native speaker.
            - `2`. A professional translator.
            - `3`. Pair of translators.

            Defaults to `3`.

        :type level: int

        :param comment:
            Optional. Context information and other relevant information
            to the translator.

        :type comment: str

        :param max_words:
            Optional. To avoid surprisingly costly orders, you can
            specify maximum word count to order. If limit is exceeded,
            the order will fail. Defaults to `1000`.

        :type max_words: int
        """
        data = {
            'group_id': group_id,
            'source_language': language,
            'target_languages': target_languages,
            'texts[][id]': texts,
            'level': kwargs.get('level', 3),
            'comment': kwargs.get('comment', ''),
            'callback_url': kwargs.get('callback_url', ''),
            'max_words': kwargs.get('max_words', 1000)
        }
        return self._authed_request('GET', 'texts/translate', data)

    def file_save(self, identifier, language, file, type, format='UTF-8',
                  save_only_data=False):
        try:
            content = file.read()
        except AttributeError:
            content = str(file)
        data = {
            'identifier': identifier,
            'language': language,
            'format': format,
            'content': base64.b64encode(content),
            'type': type,
            'save_only_data': int(save_only_data)
        }
        return self._authed_request('POST', 'file/save', data)

    def file_status(self, identifier, language):
        data = {
            'identifier': identifier,
            'language': language,
        }
        return self._authed_request('GET', 'file/status', data)

    def is_file_complete(self, identifier, language):
        status = self.file_status(identifier, language)
        return status['progress'] == '100%'

    def file_translate(self, identifier, language, target_languages, **kwargs):
        data = {
            'identifier': identifier,
            'language': language,
            'target_languages[]': target_languages,
            'level': kwargs.get('level', 3),
            'comment': kwargs.get('comment', ''),
            'callback_url': kwargs.get('callback_url', '')
        }
        return self._authed_request('POST', 'file/translate', data)

    def file_read(self, identifier, language):
        data = {
            'identifier': identifier,
            'language': language,
        }
        return self._authed_request('GET', 'file/read', data)


class TransfluentError(Exception):
    def __init__(self, response):
        data = response.json()
        self.response = response
        self.type = data['error']['type']
        self.message = data['error']['message']

    def __repr__(self):
        return '<TransfluentError [{0}]>'.format(self.type)

    def __str__(self):
        return self.message
