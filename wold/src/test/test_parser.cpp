#include <catch.hpp>
#include <iostream>
#include "../detail/parser.hpp"

namespace wold::parser {

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
      REQUIRE(parse_all(rules::identifier, s) == ast::Identifier{s});
    }
  }

  TEST_CASE("parse_expression", "[]") {
    using expr = ast::Expression;
    using infix = ast::InfixExpression;
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

  namespace {
    core::ast::Call make_call(core::ast::Expression&& callee,
                   const std::string& name_0,
                   core::ast::Expression&& arg_0,
                   const std::string& name_1,
                   core::ast::Expression&& arg_1) {
      auto call = core::ast::Call{
        std::make_unique<core::ast::Expression>(std::move(callee)),
        {}};
      call.arguments.emplace_back(name_0, std::make_unique<core::ast::Expression>(std::move(arg_0)));
      call.arguments.emplace_back(name_1, std::make_unique<core::ast::Expression>(std::move(arg_1)));
      return call;
    }
  } // namespace (anonymous)

  TEST_CASE("parse expression to_core", "[]") {
    using Literal = core::ast::Literal;
    using Identifier = core::ast::Identifier;
    using Expression = core::ast::Expression;

    REQUIRE(to_core(parse_all(rules::expression, "1")) ==
            Expression{Literal{1}});

    auto add_1_2 = Expression{make_call(
        Identifier{"__add__"},
        "lhs", Expression{Literal{1}},
        "rhs", Expression{Literal{2}})};
    REQUIRE(to_core(parse_all(rules::expression, "1 + 2")) == add_1_2);
    REQUIRE(to_core(parse_all(rules::expression, "1 + 2 - 3")) ==
            Expression{make_call(
                Identifier{"__sub__"},
                "lhs", std::move(add_1_2),
                "rhs", Expression{Literal{3}})});
  }

} // namespace wold::parser
