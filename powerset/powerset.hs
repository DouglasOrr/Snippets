-- Compute the powerset of a set (represented as a list)
--
-- e.g. docker run --rm -v `pwd`:/work -w /work haskell:8.0 runhaskell powerset.hs

ps :: [a] -> [[a]]
ps (x:xs) = rs ++ map (x:) rs where rs = ps xs
ps []     = [[]]

main :: IO ()
main = putStrLn $ show $ ps "abcd"
