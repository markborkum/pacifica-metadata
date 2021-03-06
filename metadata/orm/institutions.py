#!/usr/bin/python
"""Describes an institution and its attributes."""
from peewee import BooleanField, TextField, CharField, Expression, OP
from metadata.rest.orm import CherryPyAPI
from metadata.orm.utils import unicode_type


class Institutions(CherryPyAPI):
    """
    Institution model scribes an institute.

    Attributes:
        +-------------------+-------------------------------------+
        | Name              | Description                         |
        +===================+=====================================+
        | name              | Name of the institution             |
        +-------------------+-------------------------------------+
        | association_cd    | Type of institution (TBD)           |
        +-------------------+-------------------------------------+
        | is_foreign        | Is the institution foreign or not   |
        +-------------------+-------------------------------------+
        | encoding          | Any encoding for the name           |
        +-------------------+-------------------------------------+
    """

    name = TextField(default='')
    association_cd = CharField(default='UNK')
    is_foreign = BooleanField(default=False)
    encoding = CharField(default='UTF8')

    @staticmethod
    def elastic_mapping_builder(obj):
        """Build the elasticsearch mapping bits."""
        super(Institutions, Institutions).elastic_mapping_builder(obj)
        obj['name'] = obj['association_cd'] = \
            obj['encoding'] = {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}}
        obj['is_foreign'] = {'type': 'boolean'}

    def to_hash(self, recursion_depth=1):
        """Convert the object to a hash."""
        obj = super(Institutions, self).to_hash(recursion_depth)
        obj['_id'] = int(self.id)
        obj['name'] = unicode_type(self.name)
        obj['association_cd'] = str(self.association_cd)
        obj['is_foreign'] = bool(self.is_foreign)
        obj['encoding'] = str(self.encoding)
        return obj

    def from_hash(self, obj):
        """Convert the hash into the object."""
        super(Institutions, self).from_hash(obj)
        self._set_only_if('_id', obj, 'id', lambda: int(obj['_id']))
        self._set_only_if('name', obj, 'name', lambda: unicode_type(obj['name']))
        self._set_only_if('association_cd', obj, 'association_cd',
                          lambda: str(obj['association_cd']))
        self._set_only_if('is_foreign', obj, 'is_foreign',
                          lambda: self._bool_translate((obj['is_foreign'])))
        self._set_only_if('encoding', obj, 'encoding', lambda: str(obj['encoding']))

    @staticmethod
    def _where_attr_clause(where_clause, kwargs):
        for key in ['name', 'is_foreign', 'association_cd', 'encoding']:
            if key in kwargs:
                key_oper = OP.EQ
                if '{0}_operator'.format(key) in kwargs:
                    key_oper = getattr(OP, kwargs['{0}_operator'.format(key)].upper())
                where_clause &= Expression(getattr(Institutions, key), key_oper, kwargs[key])
        return where_clause

    def where_clause(self, kwargs):
        """PeeWee specific where clause used for search."""
        where_clause = super(Institutions, self).where_clause(kwargs)
        if '_id' in kwargs:
            where_clause &= Expression(Institutions.id, OP.EQ, kwargs['_id'])
        if 'is_foreign' in kwargs:
            kwargs['is_foreign'] = self._bool_translate(kwargs['is_foreign'])
        return self._where_attr_clause(where_clause, kwargs)
