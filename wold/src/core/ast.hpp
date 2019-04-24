#ifndef WOLD_CORE_AST_HPP
#define WOLD_CORE_AST_HPP

#include <memory>
#include <variant>
#include <vector>
#include <string>

namespace wold::core::ast {

  struct Identifier {
    std::string name;
  };

  struct Literal {
    int value;
  };

  struct Call;
  typedef std::variant<
    Literal, Identifier, Call
    > Expression;

  struct Call {
    typedef std::vector<std::tuple<std::string, std::unique_ptr<Expression>>> Arguments;
    std::unique_ptr<Expression> callee;
    Arguments arguments;
  };

  struct Definition {
    Identifier identifier;
    Expression expression;
  };

  bool operator==(const Identifier& lhs, const Identifier& rhs);
  bool operator==(const Literal& lhs, const Literal& rhs);
  bool operator==(const Call& lhs, const Call& rhs);
  bool operator==(const Definition& lhs, const Definition& rhs);

} // namespace wold::core::ast

#endif // WOLD_CORE_AST_HPP
