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

      x3::rule<class expression, ast::infix_expression> const expression = "expression";
      x3::rule<class expression_add_term, ast::infix_expression> const expression_add_term = "expression_add_term";
      x3::rule<class expression_mul_term, ast::expression> const expression_mul_term = "expression_mul_term";
      x3::rule<class add_operator, char> const add_operator = "add_operator";
      x3::rule<class mul_operator, char> const mul_operator = "mul_operator";

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

}}} // namespace wold::parser::rules

#endif //WOLD_PARSER_RULES_HPP
