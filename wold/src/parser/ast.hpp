#ifndef WOLD_PARSER_AST_HPP
#define WOLD_PARSER_AST_HPP

#include <string>
#include <boost/fusion/include/adapt_struct.hpp>
#include <boost/fusion/include/boost_tuple.hpp>
#include <boost/fusion/include/comparison.hpp>
#include <boost/fusion/include/io.hpp>
#include <boost/spirit/home/x3/support/ast/variant.hpp>


namespace wold { namespace parser { namespace ast {

      struct identifier {
        std::string name;
      };

      struct infix_expression;
      struct expression : boost::spirit::x3::variant<
        int,
        boost::spirit::x3::forward_ast<infix_expression>> {
        using base_type::base_type;
        using base_type::operator=;
      };

      struct infix_expression {
        expression first;
        std::vector<boost::tuple<char, expression>> rest;
      };

      struct definition {
        identifier identifier;
        expression expression;
      };

}}} // namespace wold::parser::ast

BOOST_FUSION_ADAPT_STRUCT(wold::parser::ast::infix_expression,
                          first, rest);
BOOST_FUSION_ADAPT_STRUCT(wold::parser::ast::identifier,
                          name);
BOOST_FUSION_ADAPT_STRUCT(wold::parser::ast::definition,
                          identifier, expression);

namespace wold { namespace parser { namespace ast {
      using boost::fusion::operator<<;
      using boost::fusion::operator==;

      inline std::ostream& operator<<(std::ostream& out, const expression& e) {
        return out << e.get();
      }

      inline std::ostream& operator<<(std::ostream& out, const infix_expression& e) {
        out << '(' << e.first;
        for (auto& next : e.rest) {
          out << ' ' << next.get<0>() << ' ' << next.get<1>();
        }
        return out << ')';
      }

      // This must come after BOOST_FUSION_ADAPT_STRUCT
      inline std::ostream& operator<<(std::ostream& out, const boost::spirit::x3::forward_ast<infix_expression>& o) {
        return out << o.get();
      }

}}} // namespace wold::parser::ast

#endif //WOLD_PARSER_AST_HPP
