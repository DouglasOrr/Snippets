'''Class decorator for defining value-like classes which use
`__slots__` to save space.
'''
import collections


_SlotSpec = collections.namedtuple('_SlotSpec', ['name', 'doc', 'init'])


def _get_slot_spec(name_or_tuple):
    if isinstance(name_or_tuple, str):
        return _SlotSpec(name_or_tuple, None, None)
    elif isinstance(name_or_tuple, (tuple, list)):
        name = name_or_tuple[0]
        doc = name_or_tuple[1] if 1 < len(name_or_tuple) else None
        init = name_or_tuple[2] if 2 < len(name_or_tuple) else None
        if not (doc is None or isinstance(doc, str)):
            raise TypeError(
                'Docstring must either be None or a str, actually %s'
                % type(doc)
            )
        if not (init is None or callable(init)):
            raise TypeError(
                'Initializer must either be None (required argument)'
                ' or a callable (argument with default), actually %s'
                % type(init)
            )
        return _SlotSpec(name, doc, init)
    else:
        raise TypeError('Expected string or tuple, actually %s.'
                        % type(name_or_tuple))


def _subclass_with_slots(type_, slot_descriptions):
    slot_specs = [_get_slot_spec(x) for x in slot_descriptions]
    base_name = type_.__name__
    patch_name = '%s_Patch' % base_name

    class Patch(type_):
        __slots__ = map(lambda x: x.name, slot_specs)

        def __init__(self, **kwargs):
            for slot in slot_specs:
                # Initialize each slot value
                if slot.init is None:
                    value = kwargs[slot.name]
                elif callable(slot.init):
                    value = kwargs.get(slot.name)
                    if value is None:
                        value = slot.init()
                setattr(self, slot.name, value)
            super(Patch, self).__init__()

        def __repr__(self):
            slot_reprs = ('%s=%r' % (slot.name, getattr(self, slot.name))
                          for slot in slot_specs)
            return '%s(%s)' % (base_name, ', '.join(slot_reprs))

    # Build a docstring describing the class slots
    doc = type_.__doc__ or ''
    doc += 'Slots (%s):\n\n' % patch_name
    for slot in slot_specs:
        doc += ' - `%s` [%s]%s\n' % (
            slot.name,
            'required' if slot.init is None else 'optional',
            (' - ' + slot.doc) if slot.doc is not None else ''
        )

    Patch.__name__ = patch_name
    Patch.__doc__ = doc
    return Patch


def slots(*slot_descriptions):
    '''Patch the given type by subclassing it, adding slots and an initializer.

    Slot descriptions may either be:

    - `str` - a named slot
    - `(str, doc)` - a named slot with a custom docstring
    - `(str, doc, init)` - a named slot with initializer and docstring

    '''
    return lambda type_: _subclass_with_slots(type_, slot_descriptions)
