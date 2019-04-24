#include "ast.hpp"

namespace wold::core::ast {

  bool operator==(const Identifier& lhs, const Identifier& rhs) {
    return lhs.name == rhs.name;
  }

  bool operator==(const Literal& lhs, const Literal& rhs) {
    return lhs.value == rhs.value;
  }

  bool operator==(const Call& lhs, const Call& rhs) {
    if (!(*lhs.callee == *rhs.callee
          && lhs.arguments.size() == rhs.arguments.size())) {
      return false;
    }
    for (auto i = 0u; i < lhs.arguments.size(); ++i) {
      if (!(std::get<0>(lhs.arguments[i]) == std::get<0>(rhs.arguments[i])
            && *std::get<1>(lhs.arguments[i]) == *std::get<1>(rhs.arguments[i]))) {
        return false;
      }
    }
    return true;
  }

  bool operator==(const Definition& lhs, const Definition& rhs) {
    return lhs.identifier == rhs.identifier
      && lhs.expression == rhs.expression;
  }

} // namespace wold::core::ast
