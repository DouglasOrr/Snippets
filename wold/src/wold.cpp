#include "wold.hpp"

#include <boost/spirit/home/x3.hpp>
#include <llvm/IR/IRBuilder.h>

namespace wold {

  int foo() {
    return 42;
  }

  float bar() {
    auto x = 5;
    return x * x;
  }

} // namespace wold
