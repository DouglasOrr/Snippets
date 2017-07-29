(ns clojure-sound-dojo.doug
  (:require [clojure-sound-dojo.player :refer [play]]
            [clojure-sound-dojo.viewer :refer [show]]))

;; Time transforms
(defn freq [f] (fn [t] (* f t)))
(defn fphase [f p] (fn [t] (+ (* f t) (p t))))

;; Waveforms
(def sine (fn [t] (Math/sin (* 2 Math/PI t))))
(def square (fn [t] (Math/signum (- (mod t 1) 0.5))))
(def sawtooth (fn [t] (- (* 2 (mod t 1)) 1)))
(def triangle
  (fn [t]
    (let [mt (mod t 1)]
      (condp > mt
        0.25 (* mt 4)
        0.75 (- 2 (* mt 4))
        (- (* mt 4) 4)))))
(def white-noise (fn [t] (- (* 2 (rand)) 1)))

(defn shape
  "Returns a waveform which linearly interprets the provided [time amplitude] pairs
  where time should be linearly increasing"
  [time-values]
  (let [segments (for [[[t0 a0] [t1 a1]] (map vector time-values (rest time-values))]
                   (fn [t] (when (<= t0 t t1)
                             (+ a0 (* (/ (- t t0) (- t1 t0))
                                      (- a1 a0))))))]
    (fn [t] (or (some #(% t) segments) 0))))

(defn adsr
  "An ADSR envelope waveform"
  [ta td ts tr slevel]
  (let [tad   (+ ta   td)
        tads  (+ tad  ts)
        tadsr (+ tads tr)]
    (shape [[0     0]
            [ta    1]
            [tad   slevel]
            [tads  slevel]
            [tadsr 0]])))

(defn mix [op & fs] (fn [t] (reduce op (map #(% t) fs))))

;; DSL
(def  |+ (partial mix +))
(def  |* (partial mix *))
(defn _ [c] (constantly c))

;; Other
(defn stereo [left right] (fn [t] [(left t) (right t)]))
(defn note [n] (* 440 (Math/pow 2 (/ n 12.0))))

;; Sounds
(defn pong [f]
  (let [env (adsr 0.1 0.2 0.1 0.1 0.1)]
    (|* env (comp sine (freq f)))))

(defn siren [f]
  (let [amp   (|+ (_ 0.6) (|* (_ 0.3) (comp sine (freq 10))))
        phase (|* (_ 10) (comp sine (freq 2)))
        wave  (comp square (fphase f phase))]
    (stereo (|* amp wave) (|* (_ -1) amp wave))))

;; Testing
(defn demo [sound duration]
  (doseq [i (range 12)]
    (play [0 duration] (sound (note i)))))

(comment
  (demo pong 0.5)
  (demo siren 1)
  )
