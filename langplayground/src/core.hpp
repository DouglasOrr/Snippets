#pragma once
#include <istream>
#include <ostream>

namespace LittleLanguage {

    struct InterpreterSettings {
        bool interactive;
        InterpreterSettings() : interactive(false) { }
    };

    bool run(std::istream& source, std::istream& in, std::ostream& out, std::ostream& err,
             const InterpreterSettings& settings);

} // namespace LittleLanguage
