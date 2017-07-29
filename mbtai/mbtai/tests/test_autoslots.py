from mbtai.autoslots import slots
from nose.tools import eq_, assert_raises
import re


@slots(
    ('foo', 'some sort of argument', None),
    ('bar', 'defaultable, yeah', lambda: 42),
    ('way', 'yet another argument', lambda: 'zzz'),
    ('fuzz', 'just a docstring'),
    'eggs',
)
class MyClass:
    '''MyClass base documentation.
    '''
    def __init__(self):
        # slots are already filled
        self.way += '_and_more'


def test_autoslots():
    x = MyClass(foo=123, way='abc', eggs='benedict', fuzz={})

    # Attribute initialization
    eq_(x.foo, 123)
    eq_(x.bar, 42)
    eq_(x.way, 'abc_and_more')
    eq_(x.fuzz, {})
    eq_(x.eggs, 'benedict')

    # String representation
    assert re.search('.+'.join(
        ['foo', '123',
         'bar', '42',
         'way', 'abc_and_more',
         'fuzz', '{}',
         'eggs', 'benedict']
    ), str(x))

    # Auto-generated type documentation
    eq_(type(x).__name__, 'MyClass_Patch')
    doc = type(x).__doc__
    assert re.search('MyClass base documentation', doc)
    assert re.search('foo.+\\[required\\].+some sort of argument', doc)
    assert re.search('bar.+\\[optional\\].+defaultable, yeah', doc)
    assert re.search('way.+\\[optional\\].+yet another argument', doc)
    assert re.search('fuzz.+\\[required\\]', doc)
    assert re.search('eggs.+\\[required\\]', doc)


def test_empty():
    @slots
    class Empty:
        pass


def test_autoslots_bad():
    with assert_raises(TypeError):
        @slots(('non_callable_init', 'docs', 123))
        class BadClass:
            pass

    with assert_raises(TypeError):
        @slots(('non_doc_str', 123))  # NOQA
        class BadClass:
            pass

    with assert_raises(TypeError):
        @slots(12345)  # NOQA
        class BadClass:
            pass
