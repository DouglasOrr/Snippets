#include "parser.hpp"

namespace wold::parser::ast {

  ////////////////////////////////////////////////////////////////////////////////
  // Conversions

  std::string get_operator_function_name(char op) {
    switch (op) {
    case '+': return "__add__";
    case '-': return "__sub__";
    case '*': return "__mul__";
    case '/': return "__div__";
    case '%': return "__mod__";
    default:
      assert(false && "unknown operator");
      return "#badname#";
    }
  }

  struct ToCoreVisitor : boost::static_visitor<core::ast::Expression> {
    core::ast::Expression operator()(int v) const {
      return core::ast::Literal{v};
    }
    core::ast::Expression operator()(const Identifier& id) const {
      return core::ast::Identifier{id.name};
    }
    core::ast::Expression operator()(const x3::forward_ast<InfixExpression>& infix) const {
      if (infix.get().rest.empty()) {
        return boost::apply_visitor(*this, infix.get().first);
      }
      auto lhs = std::make_unique<core::ast::Expression>(boost::apply_visitor(*this, infix.get().first));
      for (auto& operation : infix.get().rest) {
        auto rhs = std::make_unique<core::ast::Expression>(boost::apply_visitor(*this, boost::get<1>(operation)));
        auto call = core::ast::Call{
            std::make_unique<core::ast::Expression>(core::ast::Identifier{get_operator_function_name(boost::get<0>(operation))}),
            {}};
        call.arguments.emplace_back("lhs", std::move(lhs));
        call.arguments.emplace_back("rhs", std::move(rhs));
        lhs = std::make_unique<core::ast::Expression>(std::move(call));
      }
      return std::move(*lhs);
    }
  };

  core::ast::Expression to_core(const Expression& e) {
    return boost::apply_visitor(ToCoreVisitor(), e);
  }

  core::ast::Expression to_core(const InfixExpression& e) {
    return ToCoreVisitor()(e);
  }

  core::ast::Definition to_core(const Definition& def) {
    return core::ast::Definition{
      core::ast::Identifier{def.identifier.name},
      to_core(def.expression)};
  }

  ////////////////////////////////////////////////////////////////////////////////
  // Operators

  std::ostream& operator<<(std::ostream& out, const Expression& e) {
    return out << e.get();
  }

  std::ostream& operator<<(std::ostream& out, const InfixExpression& e) {
    out << '(' << e.first;
    for (auto& next : e.rest) {
      out << ' ' << next.get<0>() << ' ' << next.get<1>();
    }
    return out << ')';
  }

  std::ostream& operator<<(std::ostream& out, const x3::forward_ast<InfixExpression>& o) {
    return out << o.get();
  }

  bool operator==(const x3::forward_ast<InfixExpression>& left,
                  const x3::forward_ast<InfixExpression>& right) {
    return left.get() == right.get();
  }

  bool operator==(const Expression& left, const Expression& right) {
    return left.get() == right.get();
  }

} // namespace wold::parser::ast
