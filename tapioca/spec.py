#!/usr/bin/env python
# -*- coding: utf-8 -*-

from json import dumps
from tapioca.visitor import SimpleVisitor


class SpecItem(object):
    def __init__(self, description=None, *args, **kwargs):
        self.description = description


class NamedItem(SpecItem):
    def __init__(self, name=None, *args, **kwargs):
        super(NamedItem, self).__init__(*args, **kwargs)
        self.name = name


class APISpecification(SpecItem):
    def __init__(self, version=None, base_url=None):
        self.version = version
        self.base_url = base_url
        self.complete_url = '%s/%s' % (self.base_url, self.version)
        self.paths = []

    def add_path(self, path):
        self.paths.append(path)


class Path(NamedItem):
    def __init__(self, name=None, params=[], methods=[], *args, **kwargs):
        super(Path, self).__init__(name, *args, **kwargs)
        self.params = params
        self.methods = methods


class Param(NamedItem):
    def __init__(self, name=None, default_value=None, required=True,
            options=[], *args, **kwargs):
        super(Param, self).__init__(name, *args, **kwargs)
        self.default_value = default_value
        self.required = required
        self.options = options


class Method(NamedItem):
    def __init__(self, name=None, errors=[], *args, **kwargs):
        super(Method, self).__init__(name, *args, **kwargs)
        self.errors = errors


class APIError(SpecItem):
    def __init__(self, code=None, *args, **kwargs):
        super(APIError, self).__init__(*args, **kwargs)
        self.code = code


class SwaggerSpecification(SimpleVisitor):

    def __init__(self, spec):
        self.spec = spec

    def generate(self):
        return dumps(self.visit(self.spec))

    def visit_list(self, node):
        result = []
        for value in node:
            result.append(self.visit(value))
        return result

    def visit_apispecification(self, node):
        return {
            'apiVersion': node.version,
            'swaggerVersion': '1.1',
            'basePath': node.complete_url,
            'apis':  self.visit(node.paths),
            'models': []
        }

    def visit_path(self, node):
        self.current_path = node.name
        self.current_params = node.params
        return {
            'path': node.name,
            'description': '',
            'operations': self.visit(node.methods)
        }

    def visit_method(self, node):
        return {
            'httpMethod': node.name,
            'nickname': ('%s%s' % (node.name,
                self.current_path.replace('/', '_'))).lower(),
            'parameters': self.visit(self.current_params),
            'errorResponses': [],
            'summary': '',
            'notes': '',
        }

    def visit_param(self, node):
        return {
            'paramType': 'path',
            'name': node.name,
            'description': '',
            'dataType': 'String',
            'required': node.required,
            'allowMultiple': False,
        }
