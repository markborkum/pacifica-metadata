#!/usr/bin/python
"""Test the connection logic see that it works as expected."""
from unittest import TestCase
from json import dumps
from peewee import SqliteDatabase, OperationalError
from playhouse.test_utils import test_database
import httpretty
from metadata.orm import try_db_connect, DATABASE_CONNECT_ATTEMPTS, ORM_OBJECTS
import metadata.orm as metaorm


class TestConnections(TestCase):
    """Test connecting to databases make sure it works."""

    def test_db_connect_and_fail(self):
        """Try to connect to a database and fail."""
        metaorm.DB = SqliteDatabase('file:///root/foo.db')
        hit_exception = False
        try:
            try_db_connect(DATABASE_CONNECT_ATTEMPTS-1)
        except OperationalError:
            hit_exception = True
        self.assertTrue(hit_exception)

    @httpretty.activate
    def test_create_tables(self):
        """
        Test create tables.

        This is a combination of try_es_connect and
        create_elastic_index and try_db_connect
        """
        status_body = {}
        httpretty.register_uri(httpretty.GET, 'http://127.0.0.1:9200/',
                               body=dumps(status_body),
                               content_type='application/json')
        notfound_body = {}
        created_body = {
            'status': 'Created!'
        }
        httpretty.register_uri(httpretty.GET, 'http://127.0.0.1:9200/pacifica',
                               body=dumps(notfound_body),
                               content_type='application/json',
                               status=404)
        httpretty.register_uri(httpretty.PUT, 'http://127.0.0.1:9200/pacifica',
                               body=dumps(created_body),
                               content_type='application/json')
        for orm_cls in ORM_OBJECTS:
            class_name = orm_cls.__name__
            es_url = 'http://127.0.0.1:9200'
            es_mapping_url = '{0}/_mapping/{1}'.format(es_url, class_name)
            httpretty.register_uri(httpretty.PUT, es_mapping_url,
                                   body=dumps(created_body),
                                   content_type='application/json')
        with test_database(SqliteDatabase(':memory:'), ORM_OBJECTS, create_tables=False):
            metaorm.DB = SqliteDatabase(':memory:')
            metaorm.create_tables()
            self.assertTrue(httpretty.last_request().method, 'PUT')
