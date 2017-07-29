(ns balance.control
  (:require [balance.core :as bal]
            [balance.view :as view]))

;; Controllers

(defn pd-control
  "Simple proportional-derivative control"
  [{:keys [position velocity]}]
  (- (+ (* 4 (/ position Math/PI))
        velocity)))

(defn cheating-control
  "Simple 'impulse calculation' - 'how hard do I need to push to get to the top'.
  Almost 'perfect control', but ignores the effects of damping."
  [task {:keys [position velocity]}]
  (let [;; calculate energies
        {:keys [controller-torque]} task
        {:keys [center-of-mass moment-of-inertia gravity]} (:model task)
        dt                (/ bal/frame-rate)
        potential-loss    (* center-of-mass gravity (- 1 (Math/cos position)))              ; always positive
        kinetic-energy    (* 0.5 moment-of-inertia velocity velocity (bal/signum velocity)) ; signed 'energy'

        ;; calculate control
        spin-threshold    (* 0.9 (Math/asin (/ controller-torque gravity center-of-mass)))
        control-direction (if (< (Math/abs position) spin-threshold)
                            (- (bal/signum position))
                            (bal/signum velocity))
        target-kinetic    (* control-direction potential-loss)]

    (/ (- target-kinetic kinetic-energy)
       (max Float/MIN_VALUE
            (* controller-torque dt (Math/abs velocity))))))


;; Example

(defn -main
  []
  (let [task bal/task-4]
    (view/start! task pd-control)))

(comment
  (let [task bal/task-3]
    (view/start! task (partial cheating-control task)))
  )
