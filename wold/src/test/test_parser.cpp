#include <catch.hpp>
#include <iostream>
#include "../parser/rules.hpp"

namespace wold { namespace parser {

    template<class T>
    typename T::attribute_type parse_all(const T& parser, const std::string& input) {
      INFO("Parsing: \"" << input << "\"");
      typename T::attribute_type result;
      auto it = input.begin();
      auto success = boost::spirit::x3::phrase_parse(
        it, input.end(), parser, boost::spirit::x3::ascii::space, result);
      REQUIRE(success);
      REQUIRE(it == input.end());
      return result;
    }

    TEST_CASE("parse_identifier", "[]") {
      auto identifiers = {"abc", "x", "t12d", "r_an_d"};
      for (auto s : identifiers) {
        REQUIRE(parse_all(rules::identifier, s) == ast::identifier{s});
      }
    }

    TEST_CASE("parse_expression", "[]") {
      using expr = ast::expression;
      using infix = ast::infix_expression;
      REQUIRE(parse_all(rules::expression, "1 + 2 + 3 - 4") ==
              infix{
                expr{infix{expr{1}, {}}}, {
                  {'+', expr{infix{expr{2}, {}}}},
                  {'+', expr{infix{expr{3}, {}}}},
                  {'-', expr{infix{expr{4}, {}}}}
                }});
      REQUIRE(parse_all(rules::expression, "1 + 2 * 3 - 4") ==
              infix{
                expr{infix{expr{1}, {}}}, {
                  {'+', expr{infix{expr{2}, {{'*', expr{3}}}}}},
                  {'-', expr{infix{expr{4}, {}}}}
                }});
    }

}} // namespace wold::parser
