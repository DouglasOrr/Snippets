(ns interview-practise.core-test
  (:require [midje.sweet :refer :all]
            [interview-practise.core :as core]))

(def blank (core/create 3 2))

(fact "create images"
      blank => [[\O \O \O] [\O \O \O]])

(fact "show images"
      (core/show blank) => "OOO\nOOO")

(fact "clear images"
      (core/clear blank) => blank)

(fact "set-pixel"
      (-> blank (core/set-pixel 2 0 \X) core/show) => "OOX\nOOO"
      (-> blank (core/set-pixel 0 1 \X) core/show) => "OOO\nXOO")

(fact "draw-hline"
      (-> blank (core/draw-hline [1 1] 1 \R) core/show) => "OOO\nORO"
      (-> blank (core/draw-hline [1 2] 0 \R) core/show) => "ORR\nOOO"
      (-> blank (core/draw-hline [0 2] 1 \R) core/show) => "OOO\nRRR")

(fact "draw-vline"
      (-> blank (core/draw-vline 1 [1 1] \R) core/show) => "OOO\nORO"
      (-> blank (core/draw-vline 0 [0 1] \R) core/show) => "ROO\nROO"
      (-> blank (core/draw-vline 2 [0 0] \R) core/show) => "OOR\nOOO")

(fact "adjacents & flood-fill"
      (let [img [[\O \O \X] [\X \X \X]]]
        (core/adjacents img 1 0) => #{[1 0] [0 0]}
        (-> img (core/flood-fill 1 0 \R) core/show) => "RRX\nXXX"
        (core/adjacents img 2 0) => #{[2 0] [2 1] [1 1] [0 1]}
        (-> img (core/flood-fill 2 0 \R) core/show) => "OOR\nRRR"))
