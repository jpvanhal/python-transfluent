Transfluent API Client for Python
=================================

|build status|_

.. |build status| image:: https://secure.travis-ci.org/jpvanhal/python-transfluent.png?branch=master
   :alt: Build Status
.. _build status: http://travis-ci.org/jpvanhal/python-transfluent

This is a Python wrapper for the `Transfluent API <http://transfluent.com/backend-api/>`_.

Installation
------------

::

    $ pip install transfluent

Usage
-----

.. code-block:: python

    import transfluent

    # Initialize the Transfluent client and retrieve your authentication
    # token by using your email and password.
    client = transfluent.Transfluent()
    client.authenticate(email='example@example.org', password='my-password')

    # Alternatively, you may initialize the Transfluent client directly
    # with your authentication token.
    client = transfluent.Transfluent(token='my-token')

    # Order translations for a resource file.
    response = client.file_save(
        identifier='my-project/messages',
        language=1,
        file=open('translations/messages.pot'),
        type='po-file'
    )
    print "The file contains {0} words.".format(response['word_count'])
    response = client.file_translate(
        identifier='my-project/messages',
        language=1,
        target_languages=[11],
    )
    print "{0} words were ordered.".format(response['word_count'])

    # Check if the translation for the resource file is complete.
    is_translated = client.is_file_complete(
        identifier='my-project/messages',
        language=11
    )

    if is_translated:
        # Retrieve the translated resource file.
        content = client.file_read(
            identifier='my-project/messages',
            language=11
        )
        with open('translations/en/LC_MESSAGES/messages.po', 'w') as out:
            out.write(content)
    else:
        # Check the precise translation progress for the resource file.
        status = client.file_status(
            identifier='my-project/messages',
            language=11
       )
       print "Translation is {0} complete.".format(status['progress'])

Resources
---------

- `Issue Tracker <http://github.com/jpvanhal/python-transfluent/issues>`_
- `Code <http://github.com/jpvanhal/python-transfluent>`_
- `Development Version
  <http://github.com/jpvanhal/python-transfluent/zipball/master#egg=transfluent-dev>`_
