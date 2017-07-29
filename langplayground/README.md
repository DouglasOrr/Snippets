# Programming language playground

A rough playground for lambda calculus -related programming language development and learning.

## To build

You need:

 - g++
 - [Ruby](http://www.ruby-lang.org/) (rake), as we're using that as (a slightly odd) build system
 - libreadline (for the repl)
 - `$GMOCK_INCLUDE_DIR` `$GTEST_INCLUDE_DIR` `$GMOCK_LIB_DIR` (for googlemock/googletest)
 - `$BOOST_INCLUDE_DIR` (for Boost)

To get started:

        rake -T    # list tasks
        rake test  # run tests
        rake repl  # start up a repl

## The language

At the moment the language is very basic - it gives you the following lambda-calculus-like syntax (see the [grammar](LanguagePlayground/blob/master/doc/grammar.ebnf) for more detail):

        \x * 2 (+ x 3)    # is a function that adds 3 to the argument, then doubles

 - syntax is largely just `"\" "(" ")" " "`
 - only one built-in data type at the moment (integer)
 - 4 built-in functions "*" "/" "+" "-", each taking any number of arguments
   - (I think all that "/" can do at the moment is return 1, 0, or fail)

## License

This software is licensed under the [MIT license](LanguagePlayground/blob/master/LICENSE), in the unlikely event it is ever useful to anyone other than the author.
