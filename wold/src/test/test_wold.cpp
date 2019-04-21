#include <catch.hpp>
#include "../wold.hpp"
#include "../parser/rules.hpp"

#include <boost/spirit/home/x3.hpp>
#include <iostream>

namespace wold {

  TEST_CASE("parse", "[]") {
    auto text = std::string("foo0 = 103");
    REQUIRE(parse(text.begin(), text.end()));
  }

  TEST_CASE("parsing_example", "[]") {
    using boost::spirit::x3::double_;
    using boost::spirit::x3::ascii::space;

    auto text = std::string("  val 12.3 ");
    double result;
    auto success = boost::spirit::x3::phrase_parse(
        text.begin(), text.end(),
        "val" >> double_,
        space,
        result);

    REQUIRE(success);
    std::cout << result << "\n";
  }

} // namespace wold
