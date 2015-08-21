import collections


def flatten(l):
    """
    Flatten collections into one collection.
    """
    for el in l:
        try:
            if (isinstance(el, collections.Iterable)
                    and not isinstance(el, basestring)):
                for sub in flatten(el):
                    yield sub
            else:
                yield el
        except NameError:
            if (isinstance(el, collections.Iterable)
                    and not isinstance(el, str)):
                for sub in flatten(el):
                    yield sub
            else:
                yield el
