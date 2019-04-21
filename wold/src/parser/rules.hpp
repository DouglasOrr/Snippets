#ifndef WOLD_PARSER_RULES_HPP
#define WOLD_PARSER_RULES_HPP

#include "ast.hpp"
#include <boost/spirit/home/x3.hpp>

namespace wold { namespace parser { namespace rules {
      namespace x3 = boost::spirit::x3;

      // Identifier
      // - need two levels here as I can't work out how to map the rule "alpha >> *alnum"
      // directly into the wrapper class "Identifier"
      x3::rule<class identifier_string, std::string> const identifier_string = "identifier_string";
      auto const identifier_string_def = x3::lexeme[x3::alpha >> *x3::alnum];
      x3::rule<class identifier, ast::identifier> const identifier = "identifier";
      auto const identifier_def = identifier_string;

      // Expression
      x3::rule<class expression, ast::expression> const expression = "expression";
      auto const expression_def = x3::int_;

      // Definition
      x3::rule<class definition, ast::definition> const definition = "definition";
      auto const definition_def = identifier >> "=" >> expression;

      // TODO - this probably needs to be in a cpp file..?
      BOOST_SPIRIT_DEFINE(identifier_string, identifier, definition, expression);

}}} // namespace wold::parser::rules

#endif //WOLD_PARSER_RULES_HPP
