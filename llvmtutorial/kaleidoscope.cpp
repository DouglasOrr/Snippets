#include <string>
#include <cstdio>
#include <cctype>
#include <iostream>

// The lexer returns tokens [0-255] if it is an unknown character, otherwise one
// of these for known things.
enum Token {
  tok_eof = -1,
  // commands
  tok_def = -2,
  tok_extern = -3,
  // primary
  tok_identifier = -4,
  tok_number = -5,
};

static std::string IdentifierStr;
static double NumVal;

// gettok - Return the next token from standard input.
static int gettok() {
  static int LastChar = ' ';

  // Skip any whitespace
  while (std::isspace(LastChar)) {
    LastChar = std::getchar();
  }

  if (std::isalpha(LastChar)) {  // identifier: [a-zA-Z][a-zA-Z0-9]*
    IdentifierStr = LastChar;
    while (std::isalnum((LastChar = std::getchar()))) {
      IdentifierStr += LastChar;
    }

    if (IdentifierStr == "def") {
      return tok_def;
    }
    if (IdentifierStr == "extern") {
      return tok_extern;
    }
    return tok_identifier;
  }

  if (std::isdigit(LastChar) || LastChar == '.') {  // Number: [0-9.]+
    std::string NumStr;
    do {
      NumStr += LastChar;
      LastChar = std::getchar();
    } while (std::isdigit(LastChar) || LastChar == '.');

    NumVal = std::strtod(NumStr.c_str(), 0);
    return tok_number;
  }

  if (LastChar == '#') {
    // Comment until end of line
    do {
      LastChar = std::getchar();
    } while (LastChar != EOF && LastChar != '\n' && LastChar != '\r');

    if (LastChar != EOF) {
      return gettok();
    }
  }

  // Check for end of file.  Don't eat the EOF.
  if (LastChar == EOF) {
    return tok_eof;
  }

  // Otherwise, just return the character as its ascii value.
  int ThisChar = LastChar;
  LastChar = std::getchar();
  return ThisChar;
}


int main(int, char**) {
  while (true) {
    auto tok = gettok();
    std::cout << tok << std::endl;
    if (tok == tok_eof) {
      break;
    }
  }
  return 0;
}
