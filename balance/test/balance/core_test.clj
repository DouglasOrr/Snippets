(ns balance.core-test
  (:require [midje.sweet :refer :all]
            [balance.core :refer :all]))

;; TODO
;; - bar/point moment of inertia calculations
;; - alternating impulse noise

(fact "mass-height is consistent with canonical results"
      (let [model {:center-of-mass 100}]
        (mass-height model 0) => (roughly 0)
        (mass-height model (/ Math/PI 2)) => (roughly -100)
        (mass-height model (- (/ Math/PI 2))) => (roughly -100)
        (mass-height model Math/PI) => (roughly -200)
        (mass-height model (- Math/PI)) => (roughly -200)))

(fact "energy is consistent with canonical results"
      (let [model {:center-of-mass 2 :gravity 10 :moment-of-inertia 4}] ;; moment-of-inertia!
        (potential-energy model {:position 0}) => (roughly 0)
        (kinetic-energy model {:velocity 0}) => (roughly 0)
        (total-energy model {:position 0 :velocity 0}) => (roughly 0)

        (potential-energy model {:position (/ Math/PI 2)}) => (roughly -20)
        (kinetic-energy model {:velocity 3}) => (roughly 18)
        (total-energy model {:position (/ Math/PI 2) :velocity 3}) => (roughly -2)

        (total-energy model {:position Math/PI :velocity (Math/sqrt 20)}) => (roughly 0 0.0001)))

(defn state-after [model state time]
  (let [dt (double (/ (* frame-rate dynamics-frame-multiplier)))]
    (nth (iterate #(step-dynamics model 0 dt dynamics-frame-multiplier %) state)
         (* time frame-rate))))

(fact "stationary states remain stationary, unless perturbed"
      (let [model     {:gravity 10
                       :center-of-mass 1
                       :damping 0.5
                       :moment-of-inertia 1}
            at-top    (just {:position (roughly 0) :velocity (roughly 0)})
            at-bottom (just {:position (some-checker (roughly Math/PI) (roughly (- Math/PI)))
                             :velocity (roughly 0.0 0.0001)})]
        (state-after model start-stable-top 100) => at-top
        (state-after model start-stable-bottom 100) => at-bottom
        (state-after model {:position 0.01 :velocity 0} 100) => at-bottom
        (state-after model {:position 0 :velocity 0.01} 100) => at-bottom))

(fact "in a zero-damping system, energy is preserved"
      (let [task     {:model {:gravity 10
                              :center-of-mass 2
                              :damping 0
                              :moment-of-inertia 3}
                      :noise noise-none
                      :controller-torque 0
                      :start {:position 0 :velocity 0.1}}
            states   (simulate task zero-control)
            energies (->> states
                          (take (* 5 frame-rate)) ;; 5 seconds
                          (map #(total-energy (:model task) (:dynamic-state %))))]
        energies => (has every? (roughly (first energies) 0.1))))

(comment ;; performance
  ;; 100k seconds, 2M frames, 100M dynamics steps (frame-rate=20, dynamic-frame-multiplier=50)
  (time (nth (iterate (partial step task-1 zero-control) (initial-state task-1)) (* frame-rate 100000)))
  )
