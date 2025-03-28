import math

from rollbar.lib import binary_type, string_types
from rollbar.lib import (
    circular_reference_label, float_infinity_label, float_nan_label,
    undecodable_object_label, unencodable_object_label)

from rollbar.lib.transform import Transform


class SerializableTransform(Transform):
    priority = 30
    def __init__(self, safe_repr=True, safelist_types=None):
        super(SerializableTransform, self).__init__()
        self.safe_repr = safe_repr
        self.safelist = set(safelist_types or [])

    def transform_circular_reference(self, o, key=None, ref_key=None):
        return circular_reference_label(o, ref_key)

    def transform_namedtuple(self, o, key=None):
        tuple_dict = o._asdict()
        transformed_dict = self.transform_dict(tuple_dict, key=key)
        new_vals = []
        for field in tuple_dict:
            new_vals.append(transformed_dict[field])

        return '<%s>' % str(o._make(new_vals))

    def transform_number(self, o, key=None):
        if math.isnan(o):
            return float_nan_label(o)
        elif math.isinf(o):
            return float_infinity_label(o)
        else:
            return o

    def transform_bytes(self, o, key=None):
        try:
            o.decode('utf8')
        except UnicodeDecodeError:
            return undecodable_object_label(o)
        else:
            return repr(o)

    def transform_unicode(self, o, key=None):
        try:
            o.encode('utf8')
        except UnicodeEncodeError:
            return unencodable_object_label(o)
        else:
            return o

    def transform_dict(self, o, key=None):
        ret = {}
        for k, v in o.items():
            if isinstance(k, string_types) or isinstance(k, binary_type):
                if isinstance(k, bytes):
                    new_k = self.transform_bytes(k)
                else:
                    new_k = self.transform_unicode(k)
            else:
                new_k = str(k)

            ret[new_k] = v

        return super(SerializableTransform, self).transform_dict(ret, key=key)

    def transform_custom(self, o, key=None):
        if o is None:
            return None

        # Best to be very careful when we call user code in the middle of
        # preparing a stack trace. So we put a try/except around it all.
        try:
            # If the object has a __rollbar_repr__() method, use it.
            custom = Transform.rollbar_repr(o)
            if custom is not None:
                return custom

            if any(filter(lambda x: isinstance(o, x), self.safelist)):
                try:
                    return repr(o)
                except TypeError:
                    pass

            # If self.safe_repr is False, use repr() to serialize the object
            if not self.safe_repr:
                try:
                    return repr(o)
                except TypeError:
                    pass

            # Otherwise, just use the type name
            return str(type(o))

        except Exception as e:
            exc_str = ''
            try:
                exc_str = str(e)
            except Exception as e2:
                exc_str = '[%s while calling str(%s)]' % (
                    e2.__class__.__name__, e.__class__.__name__)
            return '<%s in %s.__repr__: %s>' % (
                e.__class__.__name__, o.__class__.__name__, exc_str)


__all__ = ['SerializableTransform']
