#include <catch.hpp>
#include "../wold.hpp"

namespace wold {

  TEST_CASE("foo", "[]") {
    REQUIRE(foo() == 42);
  }

} // namespace wold
