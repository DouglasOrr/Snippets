(ns clojure-sound-dojo.viewer
  (:require [incanter.core   :refer [view]]
            [incanter.charts :refer [function-plot
                                     add-function]]))

(defn show
  "Bring up a plot of the provided waveform (default range [0 1])"
  ([waveform] (show [0 1] waveform))
  ([[start end] waveform]
     (view
      (if (sequential? (waveform start))
        (reduce
         (fn [chart i]
           (add-function chart (comp #(nth % i) waveform) start end))
         (function-plot (comp first waveform) start end)
         (range 1 (count (waveform start))))
        (function-plot waveform start end)))))
