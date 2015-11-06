#!/usr/bin/env python
# encoding: utf-8
from random import randint
from tornado.testing import gen_test
from tornado.web import Application
from . import RESTTestHandler
from .server import AsyncRESTTestCase


class Handler(RESTTestHandler):
    DATA = [{i: j for i, j in enumerate(randint(0, 1000) for _ in range(100))}, '', 1]

    def get(self, *args, **kwargs):
        self.response(self.DATA)

    def delete(self, *args, **kwargs):
        self.response({'foo': []})


class TestCookies(AsyncRESTTestCase):
    def get_app(self):
        return Application(handlers=[
            ('/', Handler),
        ])

    @gen_test
    def test_imutable_dict(self):
        response = yield self.http_client.get(self.api_url.format("/"))
        assert isinstance(response.body, tuple)

    @gen_test
    def test_imutable_list(self):
        response = yield self.http_client.delete(self.api_url.format("/"))
        try:
            response.body['foo'] = 'bar'
        except TypeError:
            pass
        else:
            raise TypeError("Mutable response")

        try:
            response.body.foo = 'bar'
        except TypeError:
            pass
        else:
            raise TypeError("Mutable response")

    @gen_test
    def test_response_hash(self):
        first, second = yield [
            self.http_client.get(self.api_url.format("/")),
            self.http_client.get(self.api_url.format("/")),
        ]

        self.assertEqual(first.body, second.body)