#include <iostream>
#include <boost/multiprecision/cpp_int.hpp>
#include <sstream>
#include <unordered_map>
#include <map>
#include <limits>
using namespace std;

typedef boost::multiprecision::checked_cpp_int bigint;

namespace std {
  template<> struct hash<bigint> {
    size_t operator()(const bigint& x) const {
      auto mask = bigint(numeric_limits<size_t>::max());
      return size_t(bigint(x & mask));
    }
  };
} // namespace std

// Solve h = g^x [mod p], using a meet-in-the-middle attack
int main(int argc, char** argv) {
  if (argc <= 4) {
    cerr << "Not enough arguments, usage: ./middle p g h xmax\n"
         << "computes (x) s.t. h = g^x [mod p] | 0 < x < xmax" << endl;
  }

  // read in the parameters of the problem
  auto p = bigint(), g = bigint(), h = bigint();
  auto xmax = uint64_t();
  istringstream(argv[1]) >> p;
  istringstream(argv[2]) >> g;
  istringstream(argv[3]) >> h;
  istringstream(argv[4]) >> xmax;
  cerr << "# p=" << p << "\n# g=" << g << "\n# h=" << h << "\n# xmax=" << xmax << endl;

  // solve it
  const auto b = uint64_t(sqrt(xmax));
  const auto gb = powm(g, b, p);
  cerr << "# b=" << b << "\n# gb=" << gb << endl;

  // // build a table of the lefts
  auto lefts = unordered_map<bigint, uint64_t>();
  for (uint64_t x1 = 0; x1 <= b; ++x1) {
    auto gx1 = bigint(powm(g, x1, p));
    auto lhs = (h * bigint(powm(gx1, p-2, p))) % p;
    // cerr << lhs << endl;
    lefts.insert(make_pair(lhs, x1));
  }
  // // search for a matching right
  for (uint64_t x0 = 0; x0 <= b; ++x0) {
    auto rhs = powm(gb, x0, p);
    auto it = lefts.find(rhs);
    if (it != lefts.end()) {
      auto x1 = it->second;
      auto x = x0 * b + x1;
      cout << x << endl;
      cerr << "# Check: " << (powm(g, x, p) == h ? "OK" : "Not OK") << endl;
      return 0;
    }
  }
  cerr << "# No solution found" << endl;
  return 1;
}
