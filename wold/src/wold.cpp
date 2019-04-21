#include "wold.hpp"
#include "parser/rules.hpp"

// #include <boost/spirit/home/x3.hpp>
// #include <boost/fusion/tuple.hpp>
// #include <boost/fusion/adapted/std_tuple.hpp>
// #include <boost/fusion/include/adapt_struct.hpp>
#include <llvm/IR/IRBuilder.h>
#include <iostream>

namespace wold {

  bool parse(std::string::const_iterator begin, std::string::const_iterator end) {
    parser::ast::definition result;
    auto success = boost::spirit::x3::phrase_parse(
      begin, end, parser::rules::definition, boost::spirit::x3::ascii::space, result
    );
    std::cout << "Parsed " << result << "\n";
    return success;
  }

} // namespace wold
