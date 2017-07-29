#include "core.hpp"
#include "core_internal.hpp"
#include <iostream>
#include <readline/readline.h>
#include <readline/history.h>

using namespace std;
using namespace LittleLanguage;

int main(int /*argc*/, char** /*argv*/) {
    cout << "-------> Your REPL, sir," << endl;
    char* cline = 0;
    while ((cline = readline("> "))) {
        cout << evalLine(cline) << endl;

        if (*cline) add_history(cline);
        if (cline) {
            free(cline);
            cline = 0;
        }
    }
    cout << "<------- bye." << endl << endl;
    return 0;
}
