# Some code we're working on together:

def fibonacci_sequence n
  fibs = [1, 1]
  (n-2).times {fibs << fibs[-1] + fibs[-2]}
  fibs
end

STDOUT.puts (fibonacci_sequence 20)
