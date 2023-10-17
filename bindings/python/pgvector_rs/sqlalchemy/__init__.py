import sqlalchemy.types as types
import pgvector_rs.base as base
from functools import wraps


class Vector(types.UserDefinedType):
    cache_ok = True

    def __init__(self, dim):
        if dim < 0:
            raise ValueError("negative dim is not allowed")
        self.dim = dim

    def get_col_spec(self, **kw):
        if self.dim is None or self.dim == 0:
            return 'VECTOR'
        return 'VECTOR({})'.format(self.dim)

    def bind_processor(self, dialect):

        @base.ignore_none
        @base.valiadte_ndarray
        def _processor(value):
            if len(value) != self.dim:
                raise ValueError(
                    'invalid vector dimension for value {}'.format(value)
                )
            return base.serilize(value)

        return _processor

    def result_processor(self, dialect, coltype):

        @base.ignore_none
        @base.ignore_ndarray
        def _processor(value):
            return base.deserilize(value)

        return _processor

    class comparator_factory(types.UserDefinedType.Comparator):
        def squared_euclidean_distance(self, other):
            return self.op('<->', return_type=types.Float)(other)

        def negative_dot_product_distance(self, other):
            return self.op('<#>', return_type=types.Float)(other)

        def negative_cosine_distance(self, other):
            return self.op('<=>', return_type=types.Float)(other)