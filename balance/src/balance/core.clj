(ns balance.core
  (:require [clojure.math.numeric-tower :as math]))

;; *** constants and helpers ***

(def frame-rate 20)
(def dynamics-frame-multiplier 50)
(defn signum [x]
  (cond (< 0 x) +1
        (< x 0) -1
        :else   0))

(defn mass-height
  "Find the height of the center-of-mass (below the zero-line, where position=0)"
  [{:keys [center-of-mass]} position]
  (* center-of-mass (- (Math/cos position) 1)))

(defn potential-energy
  "Return the potential energy /kg of the system in the current state"
  [{:keys [gravity] :as model} {:keys [position]}]
  (* gravity (mass-height model position)))

(defn kinetic-energy
  "Return the kinetic energy /kg of the system in the current state"
  [{:keys [moment-of-inertia]} {:keys [velocity]}]
  (* 0.5 moment-of-inertia velocity velocity))

(defn total-energy
  "Return the total energy /kg of the system in the current state"
  [model dynamic-state]
  (+ (potential-energy model dynamic-state)
     (kinetic-energy model dynamic-state)))

;; *** dynamic model ***

(defn step-dynamics
  "Advance the dynamic state by a 'n' small increments of size 'dt', given the model & control input,
  which is fixed for the whole step."
  [{:keys [gravity center-of-mass damping moment-of-inertia]}
   input-torque dt n
   {:keys [position velocity]}]
  (let [gravity           (double gravity) ; paranoid about boxing, or Numbers.multiply(), which is slow
        center-of-mass    (double center-of-mass)
        damping           (double damping)
        moment-of-inertia (double moment-of-inertia)
        dt                (double dt)
        two-pi            (* 2 Math/PI)]
    (loop [i        n
           position (double position)
           velocity (double velocity)]
      (if (= 0 i) {:position position :velocity velocity}
          (let [torque        (+ input-torque
                                 (* gravity center-of-mass (Math/sin position))
                                 (- (* damping center-of-mass velocity)))
                acceleration  (/ torque moment-of-inertia)
                new-velocity  (+ velocity (* dt acceleration))
                new-position  (+ position (* dt new-velocity)) ; averaging new & old spoils energy conservation
                norm-position (let [n (math/round (/ new-position two-pi))]
                                (- new-position (* n two-pi)))]
            (recur (dec i) norm-position new-velocity))))))

(defn with-point-mass
  "Returns the model for a massive object on the end of a light rigid pole"
  [{:keys [length] :as model}]
  (assoc model
    :center-of-mass    length
    :moment-of-inertia (* length length)
    :type              :point))

(defn with-bar-mass
  "Returns the model for a massive rigid pole"
  [{:keys [length] :as model}]
  (assoc model
    :center-of-mass    (/ length 2)
    :moment-of-inertia (* length length (/ 3))
    :type              :bar))


;; *** overall model ***

(defn initial-state
  "Returns the starting state structure for the given task"
  [task]
  {:dynamic-state (:start task)
   :frame         0
   :control       0
   :noise         0})

(defn step
  "Advance the world's state by a single step - dynamics, controller & noise"
  [{:keys [model noise controller-torque] :as task}
   controller
   {:keys [dynamic-state frame] :as state}]
  (let [control-torque (-> (controller dynamic-state)
                           (max -1) (min 1)
                           (* controller-torque))
        noise-torque   (noise frame)
        torque         (+ control-torque noise-torque)
        dt             (/ (double (* frame-rate dynamics-frame-multiplier)))]
    {:dynamic-state (step-dynamics model torque dt dynamics-frame-multiplier dynamic-state)
     :frame         (inc frame)
     :control       control-torque
     :noise         noise-torque}))

(defn simulate
  "Generate an infinite sequence of states given a task"
  [task controller]
  (iterate (partial step task controller) (initial-state task)))

;; *** specifics ***

;; controllers
(def zero-control
  "Provides zero control input - allows system to progress naturally"
  (constantly 0))

;; models
(def model-1
  (with-point-mass {:length 2
                    :gravity 10
                    :damping 0.5}))
(def model-2
  (with-bar-mass {:length 4
                  :gravity 10
                  :damping 0.5}))
(def model-3
  (with-bar-mass {:length 2
                  :gravity 20
                  :damping 0}))
(def model-4
  (with-point-mass {:length 2
                    :gravity 10
                    :damping 4}))

;; starting conditions
(def start-stable-top {:position 0 :velocity 0})
(def start-stable-bottom {:position Math/PI :velocity 0})

;; noise
(def noise-none (constantly 0))

(defn random-seq
  [seed]
  (let [r (java.util.Random. seed)]
    (.nextDouble r)
    (repeatedly #(.nextDouble r))))

(defn noise-white
  [magnitude seed]
  (let [values (map (fn [x] (* 2 magnitude (- x 0.5)))
                    (random-seq seed))]
    (fn [frame] (nth values frame))))

(defn noise-alternating-impulse
  [interval magnitude-rate]
  (let [interval-frames (int (* interval frame-rate))]
    (fn [frame]
      (if (= 0 (mod frame interval-frames))
        (let [n (int (/ frame interval-frames))]
          (* magnitude-rate n ({0 -1 1 1} (mod n 2))))
        0))))

;; tasks
(def task-1
  {:model model-1
   :start start-stable-top
   :noise (noise-white 1 10000)
   :controller-torque 10})

(def task-2
  {:model model-2
   :start start-stable-top
   :noise (noise-alternating-impulse 0.5 0.5)
   :controller-torque 10})

(def task-3
  {:model model-3
   :start start-stable-bottom
   :noise (noise-white 2 20000)
   :controller-torque 10})

(def task-4
  {:model model-4
   :start start-stable-top
   :noise (noise-white 1 30000)
   :controller-torque 20})
