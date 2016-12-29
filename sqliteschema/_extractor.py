#!/usr/bin/env python
# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
from __future__ import unicode_literals
from collections import OrderedDict

import dataproperty as dp
import six

from ._interface import AbstractSqliteSchemaExtractor


class SqliteSchemaTextExtractorV0(AbstractSqliteSchemaExtractor):

    @property
    def verbosity_level(self):
        return 0

    def get_table_schema(self, table_name):
        return []

    def get_table_schema_text(self, table_name):
        return "{:s}\n".format(table_name)

    def _write_database_schema(self):
        for table_name in self.get_table_name_list():
            self._stream.write(self.get_table_schema_text(table_name))


class SqliteSchemaTextExtractorV1(AbstractSqliteSchemaExtractor):

    @property
    def verbosity_level(self):
        return 1

    def get_table_schema(self, table_name):
        attr_schema = self._get_attr_schema(table_name, "table")
        if attr_schema is None:
            return None

        return [
            attr.split()[0]
            for attr in attr_schema
        ]

    def get_table_schema_text(self, table_name):
        attr_list = self.get_table_schema(table_name)
        if attr_list is None:
            return None

        return "{:s} ({:s})\n".format(table_name, ", ".join(attr_list))

    def _write_database_schema(self):
        for table_name in self.get_table_name_list():
            self._stream.write(self.get_table_schema_text(table_name))


class SqliteSchemaTextExtractorV2(AbstractSqliteSchemaExtractor):

    @property
    def verbosity_level(self):
        return 2

    def get_table_schema(self, table_name):
        attr_schema = self._get_attr_schema(table_name, "table")
        if attr_schema is None:
            return None

        return OrderedDict([
            attr.split()[:2]
            for attr in attr_schema
        ])

    def get_table_schema_text(self, table_name):
        table_schema = self.get_table_schema(table_name)
        if table_schema is None:
            return None

        attr_list = []
        for key, value in six.iteritems(table_schema):
            attr_list.append("{:s} {:s}".format(key, value))

        return "{:s} ({:s})\n".format(table_name, ", ".join(attr_list))

    def _write_table_schema(self, table_name):
        self._stream.write(self.get_table_schema_text(table_name))

    def _write_database_schema(self):
        for table_name in self.get_table_name_list():
            self._write_table_schema(table_name)


class SqliteSchemaTextExtractorV3(SqliteSchemaTextExtractorV2):

    @property
    def verbosity_level(self):
        return 3

    def get_table_schema(self, table_name):
        attr_schema = self._get_attr_schema(table_name, "table")
        if attr_schema is None:
            return None

        attr_list_list = [
            attr.split()
            for attr in attr_schema
        ]
        return OrderedDict([
            [attr_list[0], " ".join(attr_list[1:])]
            for attr_list in attr_list_list
        ])


class SqliteSchemaTextExtractorV4(SqliteSchemaTextExtractorV3):

    @property
    def verbosity_level(self):
        return 4

    def get_table_schema_text(self, table_name):
        table_schema = self.get_table_schema(table_name)
        if table_schema is None:
            return None

        attr_list = []
        for key, value in six.iteritems(table_schema):
            attr_list.append("{:s} {:s}".format(key, value))

        return "\n".join([
            "{:s} (".format(table_name),
        ] + [
            ",\n".join([
                "    {:s}".format(attr)
                for attr in attr_list
            ])
        ] + [
            ")\n",
        ])

    def _write_table_schema(self, table_name):
        super(SqliteSchemaTextExtractorV4, self)._write_table_schema(
            table_name)
        self._stream.write("\n")


class SqliteSchemaTextExtractorV5(SqliteSchemaTextExtractorV4):
    __ENTRY_TYPE_LIST = ["table", "index"]

    @property
    def verbosity_level(self):
        return 5

    def get_table_schema_text(self, table_name):
        schema_text = super(
            SqliteSchemaTextExtractorV5, self).get_table_schema_text(table_name)

        index_schema = self._get_index_schema(table_name)
        if index_schema is None:
            return schema_text

        index_schema_list = [
            "{}".format(index_entry)
            for index_entry in index_schema
        ]

        if dp.is_empty_sequence(index_schema_list):
            return schema_text

        return "{:s}{:s}\n".format(schema_text, "\n".join(index_schema_list))
