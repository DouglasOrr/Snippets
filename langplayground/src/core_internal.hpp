#pragma once
#include "core.hpp"
#include "option.hpp"
#include <string>

namespace LittleLanguage {

    // Tokenize
    struct Token {
        enum Type {
            BAD_TOKEN,     // 0
            LAMBDA,        // 1
            OPEN_BRACKET,  // 2
            CLOSE_BRACKET, // 3
            IDENTIFIER,    // 4
            INTEGER        // 5
        };
        Type type;
        std::string identifierValue;
        int intValue;

        Token() : type(BAD_TOKEN) { }
    };
    typedef std::string::const_iterator char_iterator;
    char_iterator skipSpace(char_iterator pos, char_iterator end);
    char_iterator parseInteger(char_iterator pos, char_iterator end, int& result);
    char_iterator parseIdentifier(char_iterator pos, char_iterator end, std::string& result);
    char_iterator nextToken(char_iterator pos, char_iterator end, Token& result);

    // Parse
    struct Term {
        enum Type {
            BAD_TERM      = -1,
            LAMBDA        = 0,
            APPLICATION, // 1
            VARIABLE,    // 2
            INTEGER      // 3
        };

        Type type;
        Term* primaryTerm;
        Term* secondaryTerm;
        std::string variableName;
        int integerValue;

        Term();
        explicit Term(Type t);
        Term(const Term& e);
        Term& operator=(const Term& e);
        ~Term() { free(); }
    private:
        void free();
    };
    std::ostream& operator<<(std::ostream& out, const Term& expr);
    bool operator==(const Term& left, const Term& right);
    inline bool operator!=(const Term& left, const Term& right) { return !(left == right); }

    Term* lambdaTerm(const std::string& id, const Term& body);
    Term* applicationTerm(const Term& left, const Term& right);
    Term* variableTerm(const std::string& id);
    Term* integerTerm(int value);

    namespace Parse {
        struct TokenStream {
            TokenStream(const std::string& s);

            void advance();
            const Token& operator*() const { return currentToken; }
            const Token* operator->() const { return &currentToken; }
            bool good() const;

        private:
            char_iterator current, end;
            Token currentToken;
        };
        Option<Term> term(TokenStream& tokens);
        Option<Term> lambdaTerm(TokenStream& tokens);
        Option<Term> singleTerm(TokenStream& tokens);
        Option<Term> term(TokenStream& tokens);
    }

    // Top level
    // e.g.
    // (\f f (f 2)) (\x * x x);
    // (\. (. (* 2) -) 10) (\f\g\x f (g x));
    Option<Term> evalLine(const std::string& line);

} // namespace LittleLanguage
