#include "core_internal.hpp"
#include <iostream>
#include <memory>

using namespace std;

namespace LittleLanguage {
    ostream& debug() { return cerr << "[Debug] "; }

    //
    // Tokenize
    //

    char peek(char_iterator pos, char_iterator end) {
        return ++pos != end ? *pos : '\0';
    }
    char_iterator skipSpace(char_iterator pos, char_iterator end) {
        while (pos != end && !isgraph(*pos)) ++pos;
        return pos;
    }
    bool isIdentifierChar(char c) {
        return isgraph(c) && c != '(' && c != ')' && c != '\\';
    }
    char_iterator parseInteger(char_iterator pos, char_iterator end, int& result) {
        stringstream numStr;
        do {
            numStr.put(*pos);
        } while (pos != end && isdigit(*(++pos)));
        numStr >> result;
        assert(numStr.eof() && "after reading the value, the stream should be empty");
        return pos;
    }
    char_iterator parseIdentifier(char_iterator pos, char_iterator end, string& result) {
        result.clear();
        do {
            result.push_back(*pos);
        } while (pos != end && isIdentifierChar(*(++pos)));
        return pos;
    }
    char_iterator nextToken(char_iterator pos, char_iterator end, Token& result) {
        if (pos != end) {
            if (!isgraph(*pos)) pos = skipSpace(++pos, end);

            char c = *pos;
            if      (c == '(')  { result.type = Token::OPEN_BRACKET; ++pos; }
            else if (c == ')')  { result.type = Token::CLOSE_BRACKET; ++pos; }
            else if (c == '\\') { result.type = Token::LAMBDA; ++pos; }
            else if (isdigit(c) || (c == '-' && isdigit(peek(pos, end)))) {
                result.type = Token::INTEGER;
                pos = parseInteger(pos, end, result.intValue);
            } else {
                result.type = Token::IDENTIFIER;
                pos = parseIdentifier(pos, end, result.identifierValue);
            }
            return skipSpace(pos, end);

        } else {
            result = Token();
            return pos;
        }
    }

    //
    // Term
    //

    Term::Term()
        : type(BAD_TERM), primaryTerm(0), secondaryTerm(0) { }

    Term::Term(Type t)
        : type(t), primaryTerm(0), secondaryTerm(0) { }

    Term::Term(const Term& e)
        : type(e.type),
          primaryTerm(e.primaryTerm ? new Term(*e.primaryTerm) : 0),
          secondaryTerm(e.secondaryTerm ? new Term(*e.secondaryTerm) : 0),
          variableName(e.variableName),
          integerValue(e.integerValue) { }

    Term& Term::operator=(const Term& e) {
        if (&e != this) {
            free();
            primaryTerm = e.primaryTerm ? new Term(*e.primaryTerm) : 0;
            secondaryTerm = e.secondaryTerm ? new Term(*e.secondaryTerm) : 0;
        }
        return *this;
    }

    void Term::free() {
        if (primaryTerm) delete primaryTerm;
        if (secondaryTerm) delete secondaryTerm;
    }

    ostream& operator<<(ostream& out, const Term& term) {
        // Prints in a LISP-like tree representation
        if (term.type == Term::LAMBDA) {
            out << "(fn [" << term.variableName << "] "
                << *(term.primaryTerm) << ")";

        } else if (term.type == Term::APPLICATION) {
            out << "(" << *(term.primaryTerm) << " "
                << *(term.secondaryTerm) << ")";

        } else if (term.type == Term::VARIABLE) {
            out << term.variableName;

        } else if (term.type == Term::INTEGER) {
            out << term.integerValue;

        } else assert(false && "unknown Term type");

        return out;
    }

    bool operator==(const Term& left, const Term& right) {
        if (left.type != right.type) {
            return false;

        } else if (left.type == Term::LAMBDA) {
            assert(left.primaryTerm && right.primaryTerm);
            return left.variableName == right.variableName &&
                *(left.primaryTerm) == *(right.primaryTerm);

        } else if (left.type == Term::APPLICATION) {
            assert(left.primaryTerm && right.primaryTerm &&
                   left.secondaryTerm && right.secondaryTerm);
            return *(left.primaryTerm) == *(right.primaryTerm) &&
                *(left.secondaryTerm) == *(right.secondaryTerm);

        } else if (left.type == Term::VARIABLE) {
            return left.variableName == right.variableName;

        } else if (left.type == Term::INTEGER) {
            return left.integerValue == right.integerValue;

        } else {
            assert(false && "unknown Term type");
            return false;
        }
    }

    //
    // Parse & eval
    //

    Option<Term> errorTerm(const string& message) {
        Option<Term> result;
        result.err() << message;
        return result;
    }

    Term* lambdaTerm(const string& id, const Term& body) {
        Term* result = new Term(Term::LAMBDA);
        result->variableName = id;
        result->primaryTerm = new Term(body);
        return result;
    }

    Term* bindTerm(const string& bindingName, const Term& bindingTerm, const Term& term) {
        if (term.type == Term::LAMBDA) {
            if (term.variableName != bindingName) {
                unique_ptr<Term> newBody(bindTerm(bindingName, bindingTerm, *(term.primaryTerm)));
                return lambdaTerm(term.variableName, *newBody);
            } else return new Term(term);

        } else if (term.type == Term::APPLICATION) {
            unique_ptr<Term> left(bindTerm(bindingName, bindingTerm, *(term.primaryTerm)));
            unique_ptr<Term> right(bindTerm(bindingName, bindingTerm, *(term.secondaryTerm)));
            return applicationTerm(*left, *right);

        } else if (term.type == Term::VARIABLE) {
            if (term.variableName == bindingName) {
                return new Term(bindingTerm);
            } else return new Term(term);

        } else if (term.type == Term::INTEGER) {
            return new Term(term);

        } else assert(false && "unknown Term type");
    }

    Term* applicationTerm(const Term& left, const Term& right) {
        if (left.type == Term::INTEGER && right.type == Term::INTEGER &&
            (left.variableName == "*" || left.variableName == "/" ||
             left.variableName == "+" || left.variableName == "-")) { // a built-in

            Term* result = new Term(Term::INTEGER);
            result->integerValue = left.integerValue;
            if      (left.variableName == "*") result->integerValue *= right.integerValue;
            else if (left.variableName == "/") result->integerValue /= right.integerValue;
            else if (left.variableName == "+") result->integerValue += right.integerValue;
            else if (left.variableName == "-") result->integerValue -= right.integerValue;
            else assert(false && "unknown built-in operation");
            result->variableName = left.variableName;
            return result;

        } else if (left.type == Term::LAMBDA) {
            return bindTerm(left.variableName, right, *(left.primaryTerm));

        } else {
            Term* result = new Term(Term::APPLICATION);
            result->primaryTerm = new Term(left);
            result->secondaryTerm = new Term(right);
            return result;
        }
    }

    Term* variableTerm(const string& id) {
        if (id == "*" || id == "/" || id == "+" || id == "-") {
            Term* result = new Term(Term::INTEGER);
            result->integerValue = (id == "*" || id == "/") ? 1 : 0;
            result->variableName = id;
            return result;

        } else {
            Term* result = new Term(Term::VARIABLE);
            result->variableName = id;
            return result;
        }
    }

    Term* integerTerm(int value) {
        Term* result = new Term(Term::INTEGER);
        result->integerValue = value;
        return result;
    }

    namespace Parse {
        TokenStream::TokenStream(const string& s)
            : end(s.end()) {
            current = nextToken(s.begin(), s.end(), currentToken);
        }

        void TokenStream::advance() {
            if (current != end) {
                current = nextToken(current, end, currentToken);
            } else currentToken = Token(); // BAD_TOKEN
        }

        bool TokenStream::good() const {
            return currentToken.type != Token::BAD_TOKEN;
        }

        Option<Term> lambdaTerm(TokenStream& tokens) {
            assert(tokens->type == Token::LAMBDA);
            tokens.advance();

            if (tokens->type == Token::IDENTIFIER) {
                string id = tokens->identifierValue;
                tokens.advance();
                Option<Term> body = term(tokens);
                if (body.exists()) {
                    return Option<Term>(lambdaTerm(id, *body));

                } else return body;
            } else return errorTerm("expected identifier");
        }

        Option<Term> singleTerm(TokenStream& tokens) {
            if (tokens->type == Token::LAMBDA) {
                return lambdaTerm(tokens);

            } else if (tokens->type == Token::OPEN_BRACKET) {
                tokens.advance();
                Option<Term> t = term(tokens);
                if (tokens->type == Token::CLOSE_BRACKET) {
                    tokens.advance();
                    return t;
                } else return errorTerm("expected closing bracket");

            } else if (tokens->type == Token::IDENTIFIER) {
                string id = tokens->identifierValue;
                tokens.advance();
                return Option<Term>(variableTerm(id));

            } else if (tokens->type == Token::INTEGER) {
                int value = tokens->intValue;
                tokens.advance();
                return Option<Term>(integerTerm(value));

            } else if (tokens->type == Token::CLOSE_BRACKET) {
                return errorTerm("unexpected closing bracket");

            } else if (!tokens.good()) {
                return errorTerm("expected a term");
            } else return errorTerm("unknown token");
        }

        Option<Term> term(TokenStream& tokens) {
            Option<Term> current = singleTerm(tokens);
            if (current.exists()) {
                while (tokens.good() && tokens->type != Token::CLOSE_BRACKET) {
                    Option<Term> next = singleTerm(tokens);
                    if (next.exists()) {
                        current = Option<Term>(applicationTerm(*current, *next));
                    } else return next;
                }
                return current;
            } else return current;
        }
    } // namespace Parse

    //
    // Top level
    //

    Option<Term> evalLine(const string& line) {
        Parse::TokenStream tokens(line);
        return tokens.good() ? Parse::term(tokens) : errorTerm("no input");
    }

    bool run(istream& source, istream& /*in*/, ostream& out, ostream& err,
             const InterpreterSettings& settings) {
        bool ok = true;
        while (ok && source.good()) {
            if (settings.interactive) out << "> ";
            string line;
            getline(source, line, ';');
            Option<Term> term = evalLine(line);

            if (term.exists()) {
                err << *term << endl;
            } else {
                err << "[Error] eval fail... " << term.errorMessage() << endl;
                ok = false;
            }
        }
        return ok;
    }

} // namespace LittleLanguage
