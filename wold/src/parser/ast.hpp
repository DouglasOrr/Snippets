#ifndef WOLD_PARSER_AST_HPP
#define WOLD_PARSER_AST_HPP

#include <string>
#include <boost/fusion/include/adapt_struct.hpp>
#include <boost/fusion/include/io.hpp>

namespace wold { namespace parser { namespace ast {

      struct identifier {
        std::string name;
      };

      typedef int expression;

      struct definition {
        identifier identifier;
        expression expression;
      };

      using boost::fusion::operator<<;

}}} // namespace wold::parser::ast

BOOST_FUSION_ADAPT_STRUCT(wold::parser::ast::identifier,
                          name);
BOOST_FUSION_ADAPT_STRUCT(wold::parser::ast::definition,
                          identifier, expression);

#endif //WOLD_PARSER_AST_HPP
