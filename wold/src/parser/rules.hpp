#ifndef WOLD_PARSER_RULES_HPP
#define WOLD_PARSER_RULES_HPP

#include "ast.hpp"
#include <boost/spirit/home/x3.hpp>

namespace wold { namespace parser { namespace rules {
      namespace x3 = boost::spirit::x3;

      // Need two levels for "identifier" as I can't work out how to map the rule
      // directly into the attribute wrapper class "identifier"
      x3::rule<class identifier_string, std::string> const identifier_string = "identifier_string";
      x3::rule<class identifier, ast::identifier> const identifier = "identifier";
      x3::rule<class definition, ast::definition> const definition = "definition";

      x3::rule<class expression, ast::expression> const expression = "expression";
      x3::rule<class expression_term_add, ast::expression> const expression_term_add = "expression_term_add";
      x3::rule<class expression_term_mul, ast::expression> const expression_term_mul = "expression_term_mul";
      x3::rule<class add_operator, char> const add_operator = "add_operator";
      x3::rule<class mul_operator, char> const mul_operator = "mul_operator";
      x3::rule<class infix_expression_add, ast::infix_expression> const infix_expression_add = "infix_expression_add";
      x3::rule<class infix_expression_mul, ast::infix_expression> const infix_expression_mul = "infix_expression_mul";

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
        infix_expression_add | expression_term_add;
      auto const add_operator_def =
        x3::char_('+') | x3::char_('-');
      auto const infix_expression_add_def =
        expression_term_add >> +(add_operator >> expression_term_add);
      auto const expression_term_add_def =
        infix_expression_mul | expression_term_mul;
      auto const mul_operator_def =
        x3::char_('*') | x3::char_('/') | x3::char_('%');
      auto const infix_expression_mul_def =
        expression_term_mul >> +(mul_operator >> expression_term_mul);
      auto const expression_term_mul_def =
        x3::int_ | ('(' >> expression >> ')');

      BOOST_SPIRIT_DEFINE(
        identifier_string, identifier,
        expression, expression_term_add, expression_term_mul,
        add_operator, mul_operator,
        infix_expression_mul, infix_expression_add,
        definition);

}}} // namespace wold::parser::rules

#endif //WOLD_PARSER_RULES_HPP
