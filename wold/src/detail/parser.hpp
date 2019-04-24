#ifndef WOLD_DETAIL_PARSER_HPP
#define WOLD_DETAIL_PARSER_HPP

#include "../ast.hpp"

#include <string>
#include <vector>
#include <boost/fusion/include/adapt_struct.hpp>
#include <boost/fusion/include/boost_tuple.hpp>
#include <boost/fusion/include/comparison.hpp>
#include <boost/fusion/include/io.hpp>
#include <boost/spirit/home/x3.hpp>
#include <boost/spirit/home/x3/support/ast/variant.hpp>

namespace wold::parser::ast {
  namespace x3 = boost::spirit::x3;

  struct Identifier {
    std::string name;
  };

  struct InfixExpression;
  struct Expression : x3::variant<
    int,
    Identifier,
    x3::forward_ast<InfixExpression>> {
    using base_type::base_type;
    using base_type::operator=;
  };

  struct InfixExpression {
    Expression first;
    std::vector<boost::tuple<char, Expression>> rest;
  };

  struct Definition {
    Identifier identifier;
    Expression expression;
  };

  core::ast::Expression to_core(const Expression&);
  core::ast::Expression to_core(const InfixExpression&);
  core::ast::Definition to_core(const Definition&);

  using boost::fusion::operator<<;
  std::ostream& operator<<(std::ostream& out, const Expression& e);
  std::ostream& operator<<(std::ostream& out, const InfixExpression& e);
  std::ostream& operator<<(std::ostream& out, const x3::forward_ast<InfixExpression>& o);

  using boost::fusion::operator==;
  bool operator==(const Expression& left, const Expression& right);
  bool operator==(const x3::forward_ast<InfixExpression>& left,
                  const x3::forward_ast<InfixExpression>& right);

} // namespace wold::parser::ast

BOOST_FUSION_ADAPT_STRUCT(wold::parser::ast::InfixExpression,
                          first, rest);
BOOST_FUSION_ADAPT_STRUCT(wold::parser::ast::Identifier,
                          name);
BOOST_FUSION_ADAPT_STRUCT(wold::parser::ast::Definition,
                          identifier, expression);

namespace wold::parser::rules {
  namespace x3 = boost::spirit::x3;

  // Need two levels for "Identifier" as I can't work out how to map the rule
  // directly into the attribute wrapper class "Identifier"
  x3::rule<class IdentifierString, std::string> const identifier_string = "identifier_string";
  x3::rule<class Identifier, ast::Identifier> const identifier = "identifier";
  x3::rule<class Definition, ast::Definition> const definition = "definition";

  x3::rule<class Expression, ast::InfixExpression> const expression = "expression";
  x3::rule<class ExpressionAddTerm, ast::InfixExpression> const expression_add_term = "expression_add_term";
  x3::rule<class ExpressionMulTerm, ast::Expression> const expression_mul_term = "expression_mul_term";
  x3::rule<class AddOperator, char> const add_operator = "add_operator";
  x3::rule<class MulOperator, char> const mul_operator = "mul_operator";

  // Grammar
  auto const identifier_char =
    x3::char_('a', 'z') | x3::char_('A', 'Z') | x3::char_('0', '9') | x3::char_('_');
  auto const identifier_string_def = x3::lexeme[
    (identifier_char - x3::char_('0', '9'))
    >> *identifier_char
    >> &-identifier_char
    ];
  auto const identifier_def = identifier_string;
  auto const definition_def = identifier >> "=" >> expression;

  auto const expression_def =
    expression_add_term >> *(add_operator >> expression_add_term);
  auto const expression_add_term_def =
    expression_mul_term >> *(mul_operator >> expression_mul_term);
  auto const expression_mul_term_def =
    x3::int_ | identifier | ('(' >> expression >> ')');
  auto const add_operator_def =
    x3::char_('+') | x3::char_('-');
  auto const mul_operator_def =
    x3::char_('*') | x3::char_('/') | x3::char_('%');

  BOOST_SPIRIT_DEFINE(
    identifier_string, identifier,
    expression, expression_add_term, expression_mul_term,
    add_operator, mul_operator,
    definition);

} // namespace wold::parser::rules

#endif //WOLD_DETAIL_PARSER_HPP
