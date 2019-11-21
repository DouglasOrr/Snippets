# Wold grammar

```ebnf
id_letter = ?a-z? | ?A-Z? | "_";
digit = ?0-9?;

identifier = id_letter, {id_letter | digit};
integer = ["-"], digit, {digit};

expresion = expression_add_term, {("+" | "-"), expression_add_term};
expression_add_term = expression_mul_term, {("*" | "/" | "%"), expression_mul_term};
expression_mul_term = integer | identifier | ("(", expression, ")");

definition = identifier, "=", expression;
```
