#include "option.hpp"
#include "core_internal.hpp"
#include <gtest/gtest.h>
#include <memory>
#include <list>

using namespace std;
using namespace LittleLanguage;

TEST(OptionTest, SuccessAndFailure) {
    Option<const int> fail;
    EXPECT_FALSE(fail.exists());
    EXPECT_TRUE(!fail);
    EXPECT_EQ("", fail.errorMessage());
    fail.err() << "Oh dear, " << 1 << " didn't work";
    EXPECT_EQ("Oh dear, 1 didn't work", fail.errorMessage());

    Option<const int> reassigned(new int(42));
    EXPECT_TRUE(reassigned.exists());
    EXPECT_EQ(42, *reassigned);

    Option<const int> copy = reassigned;
    reassigned = fail;
    EXPECT_FALSE(reassigned.exists());
    EXPECT_TRUE(copy.exists());
    EXPECT_EQ(42, *copy);
}

TEST(TokenizeTest, SkipSpace) {
    string test(" \t\r\n  a b");
    char_iterator a = skipSpace(test.begin(), test.end());
    EXPECT_EQ('a', *a);
    EXPECT_EQ('a', *skipSpace(a, test.end()));
    EXPECT_EQ('b', *skipSpace(a + 1, test.end()));
}

TEST(TokenizeTest, ParseInteger) {
    string test("123(");
    int i = 0;
    EXPECT_EQ('(', *parseInteger(test.begin(), test.end(), i));
    EXPECT_EQ(123, i);
}

TEST(TokenizeTest, ParseNegativeInteger) {
    string test("-123");
    int i = 0;
    EXPECT_TRUE(test.end() == parseInteger(test.begin(), test.end(), i));
    EXPECT_EQ(-123, i);
}

TEST(TokenizeTest, ParseIdentifier) {
    string test("abc\\d");
    string id;
    EXPECT_EQ('\\', *parseIdentifier(test.begin(), test.end(), id));
    EXPECT_EQ("abc", id);
}

TEST(TokenizeTest, NextToken) {
    string test("  \\x\\rest(* -23 4 x)");
    char_iterator it = test.begin();
    Token t;

    it = nextToken(it, test.end(), t);
    EXPECT_EQ(Token::LAMBDA, t.type);

    it = nextToken(it, test.end(), t);
    EXPECT_EQ(Token::IDENTIFIER, t.type);
    EXPECT_EQ("x", t.identifierValue);

    it = nextToken(it, test.end(), t);
    EXPECT_EQ(Token::LAMBDA, t.type);

    it = nextToken(it, test.end(), t);
    EXPECT_EQ(Token::IDENTIFIER, t.type);
    EXPECT_EQ("rest", t.identifierValue);

    it = nextToken(it, test.end(), t);
    EXPECT_EQ(Token::OPEN_BRACKET, t.type);

    it = nextToken(it, test.end(), t);
    EXPECT_EQ(Token::IDENTIFIER, t.type);
    EXPECT_EQ("*", t.identifierValue);

    it = nextToken(it, test.end(), t);
    EXPECT_EQ(Token::INTEGER, t.type);
    EXPECT_EQ(-23, t.intValue);

    it = nextToken(it, test.end(), t);
    EXPECT_EQ(Token::INTEGER, t.type);
    EXPECT_EQ(4, t.intValue);

    it = nextToken(it, test.end(), t);
    EXPECT_EQ(Token::IDENTIFIER, t.type);
    EXPECT_EQ("x", t.identifierValue);

    it = nextToken(it, test.end(), t);
    EXPECT_EQ(Token::CLOSE_BRACKET, t.type);
}

TEST(TermTest, Equality) {
    unique_ptr<Term> int1(integerTerm(42));
    unique_ptr<Term> int1b(integerTerm(42));
    unique_ptr<Term> int2(integerTerm(43));
    unique_ptr<Term> lam1(lambdaTerm("x", *int1));
    unique_ptr<Term> lam2(lambdaTerm("y", *int1));
    unique_ptr<Term> app1(applicationTerm(*lam1, *int1));
    unique_ptr<Term> app1b(applicationTerm(*lam1, *int1b));

    EXPECT_EQ(*int1, *int1b);
    EXPECT_NE(*int1, *int2);

    EXPECT_EQ(*lam1, *lam1);
    EXPECT_NE(*lam1, *lam2);
    EXPECT_NE(*lam1, *int1);
    EXPECT_NE(*int1, *lam1);

    EXPECT_EQ(*app1, *app1b); // definitely not just pointer equality
}

namespace {
    struct Pool {
        virtual ~Pool() {
            for (list<Term*>::const_iterator it = m_values.begin(); it != m_values.end(); ++it) {
                delete *it;
            }
        }
        const Term& pool(Term* e) {
            m_values.push_back(e);
            return *e;
        }

    private:
        list<Term*> m_values;
    };

} // namespace (anonymous)

struct ParseTest : public ::testing::Test, public Pool {

    Option<Term> eval(string input) {
        Parse::TokenStream tokens(input);
        return Parse::term(tokens);
    }
};

TEST_F(ParseTest, TokenStream) {
    string test = "\\a 1";
    Parse::TokenStream tokens(test);

    EXPECT_TRUE(tokens.good());
    EXPECT_EQ(Token::LAMBDA, tokens->type);

    tokens.advance();
    EXPECT_TRUE(tokens.good());
    EXPECT_EQ(Token::IDENTIFIER, tokens->type);

    tokens.advance();
    EXPECT_TRUE(tokens.good());
    EXPECT_EQ(Token::INTEGER, tokens->type);

    tokens.advance();
    EXPECT_FALSE(tokens.good());
}

TEST_F(ParseTest, IntegerTerm) {
    string testString = " 12 a";
    Parse::TokenStream test(testString);

    Option<Term> e = Parse::singleTerm(test);
    ASSERT_TRUE(e.exists()) << e;
    EXPECT_EQ(pool(integerTerm(12)), *e);

    EXPECT_EQ(Token::IDENTIFIER, test->type)
        << "after parsing, the stream should point at the next available token";
}

TEST_F(ParseTest, VariableTerm) {
    string testString = "abc \\";
    Parse::TokenStream test(testString);

    Option<Term> e = Parse::singleTerm(test);
    ASSERT_TRUE(e.exists()) << e;
    EXPECT_EQ(pool(variableTerm("abc")), *e);

    EXPECT_EQ(Token::LAMBDA, test->type)
        << "after parsing, the stream should point at the next available token";
}

TEST_F(ParseTest, ApplicationTerm) {
    string testString = "f 1 2 ";
    Parse::TokenStream test(testString);

    Option<Term> e = Parse::term(test);
    ASSERT_TRUE(e.exists()) << e;
    EXPECT_EQ(
        pool(applicationTerm(
            pool(applicationTerm(
                pool(variableTerm("f")),
                pool(integerTerm(1)))),
            pool(integerTerm(2)))),
        *e);

    EXPECT_FALSE(test.good()) << "we should be at the end now";
}

TEST_F(ParseTest, LambdaTerm) {
    string testString = "\\x\\y y x";
    Parse::TokenStream test(testString);

    Option<Term> e = Parse::term(test);
    ASSERT_TRUE(e.exists()) << e;
    EXPECT_EQ(
        pool(lambdaTerm("x",
            pool(lambdaTerm("y",
                pool(applicationTerm(
                    pool(variableTerm("y")),
                    pool(variableTerm("x")))))))),
        *e);

    EXPECT_FALSE(test.good()) << "we should be at the end now";
}

TEST_F(ParseTest, BrackettedTerm) {
    string testString = "(+ 1) a";
    Parse::TokenStream test(testString);

    Option<Term> e = Parse::singleTerm(test);
    ASSERT_TRUE(e.exists()) << e;
    EXPECT_EQ(
        pool(applicationTerm(
            pool(variableTerm("+")),
            pool(integerTerm(1)))),
        *e);

    EXPECT_EQ(Token::IDENTIFIER, test->type)
        << "after parsing, the stream should point at the next available token";
}

TEST_F(ParseTest, SimpleEval) {
    Option<Term> e = eval("(\\f f (f 2)) (\\x * x x)");
    ASSERT_TRUE(e.exists()) << e;
    EXPECT_EQ(pool(integerTerm(16)), *e);
}

TEST_F(ParseTest, CompositionEval) {
    // defines composition, and binds it to '.'
    Option<Term> e = eval("(\\. (. (* 2) -) 10) (\\f\\g\\x f (g x))");
    ASSERT_TRUE(e.exists()) << e;
    EXPECT_EQ(pool(integerTerm(-20)), *e);
}

int main(int argc, char* argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
