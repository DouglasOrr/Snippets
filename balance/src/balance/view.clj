(ns balance.view
  (:require [quil.core      :as q]
            [quil.applet    :as qa]
            [balance.core   :as bal]))

(declare view! task-var step-var states-var paused-var mouse-control)

;; Top-level operations

(defn start!
  "Begin a live simulation using the given controller (with mouse override)"
  ([task] (start! task bal/zero-control))
  ([task controller]
     (dosync
      (ref-set task-var task)
      (ref-set step-var (partial bal/step task (mouse-control controller)))
      (ref-set states-var (list (bal/initial-state task)))
      (ref-set paused-var false))
     (view!)))

(defn playback!
  "Playback a simulation using the finite sequence of states provided"
  [task states]
  (let [states-vec (vec states)]
    (dosync
     (ref-set task-var task)
     (ref-set step-var (fn [{:keys [frame]}]
                         (get states-vec (inc frame))))
     (ref-set states-var (take 1 states))
     (ref-set paused-var false))
    (view!)))

;; Utility

(def printer-agent (agent *out*))
(defn puts
  "Like println, but use an agent to ensure that output goes to the nrepl buffer"
  [& args]
  (send printer-agent
        (fn [out] (doto out
                    (.print (apply prn-str args))
                    .flush))))

;; Settings

(def graph-duration 8.0)
(def ghost-interval 0.2)
(def ghost-lifetime 0.8)

;; Controllers

(defn mouse-control
  "Create a controller that first checks if mouse-left or mouse-right is pressed,
  otherwise delegates to the provided background controller."
  ([] (mouse-control bal/zero-control))
  ([background-control]
     (fn [x]
       (if (q/mouse-state)
         ({:left -1 :right 1} (q/mouse-button))
         (background-control x)))))

;; Model

(defonce task-var (ref nil))
(defonce step-var (ref nil))
(defonce states-var (ref nil))
(defonce paused-var (ref true))

(defn step!
  "Advance by a single frame (keeping a full history of previous states)"
  []
  (let [[state :as states] @states-var
        new-state (@step-var state)]
    (if new-state
      (ref-set states-var (cons new-state states))
      (ref-set paused-var true))))

(defn unstep!
  "Reverse a step, using the state history"
  []
  (when (< 1 (count @states-var))
    (ref-set states-var (rest @states-var))))

;; Model accessors

(def control-graph-frames (* graph-duration bal/frame-rate))
(def ghost-interval-frames (int (* ghost-interval bal/frame-rate)))
(def ghost-lifetime-frames (int (* ghost-lifetime bal/frame-rate)))

(defn controller-torque [] (-> @task-var :controller-torque))
(defn model-type []        (-> @task-var :model :type))
(defn current-state []     (-> @states-var first :dynamic-state))
(defn current-control []   (-> @states-var first :control))
(defn control-noise-graph []
  (->> @states-var
       (take control-graph-frames)
       (map (juxt :control :noise))))
(defn ghosts []
  (let [states @states-var
        offset (mod (count states) ghost-interval-frames)]
    (->> states
         (map-indexed vector)
         (drop offset)
         (take-nth ghost-interval-frames)
         (map (fn [[age state]]
                [(-> state :dynamic-state :position)
                 (- 1 (/ age ghost-lifetime-frames))]))
         (take-while (fn [[_ life]] (< 0 life))))))

;; View

(def line-len 300)
(def blob-size 20)
(def margin 20)
(def control-height 20)
(def graph-width 200)

(defn width [] (- (q/width) (* 2 margin)))
(defn height [] (- (q/height) (* 2 margin)))
(defn left [] margin)
(defn bottom [] (- (q/height) margin))
(defn right [] (- (q/width) margin))
(defn top [] margin)

(defn pole-top [] (+ (top) control-height margin (/ blob-size 2)))
(defn graph-left [] (+ (left) (* 2 line-len) margin (/ blob-size 2)))

(defn ^:dynamic setup!
  []
  (q/frame-rate bal/frame-rate)
  (q/smooth)
  (q/text-size 16))

(defn draw-pole!
  [pole-type shade theta]
  (q/stroke-weight ({:point 2 :bar 10} pole-type))
  (q/stroke shade)
  (q/fill shade)
  (let [[ox oy] [(+ (left) line-len) (+ (pole-top) line-len)]
        [dx dy] [(Math/sin theta) (Math/cos theta)]
        [cx cy] [(+ ox (* line-len dx)) (- oy (* line-len dy))]
        [px py] (if (= :point pole-type)
                  [(- cx (* 0.5 blob-size dx)) (+ cy (* 0.5 blob-size dy))]
                  [cx cy])]
    (q/line ox oy px py)
    (when (= :point pole-type)
      (q/ellipse cx cy blob-size blob-size))))

(defn draw-control!
  [torque]
  (let [control (/ torque (controller-torque))]
    (q/stroke-weight 0)
    (q/fill 128)
    (let [ox (+ (left) line-len)
          oy (top)
          w  (* line-len control)]
      (cond (< 0 control) (q/rect ox oy w control-height)
            (< control 0) (q/rect (+ ox w) oy (- w) control-height)))))

(defn draw-graph!
  [torques]
  (let [norm (->> torques
                  (map (fn [samples] (apply max (map #(Math/abs %) samples))))
                  (cons (controller-torque))
                  (apply max))
        dy   (/ (height) (float control-graph-frames))
        getx #(-> % (/ norm) inc (* (/ 2) graph-width) (+ (graph-left)))]
    (q/stroke-weight 1)
    (q/stroke (q/color 0 0 255 64))
    (doseq [x (map getx [(- norm) 0 norm])]
      (q/line x (top) x (bottom)))
    (doseq [[[a0 b0] [a1 b1] y0] (map vector torques (rest torques) (iterate #(+ % dy) (top)))
            :let [y1 (+ y0 dy)]]
      (q/stroke (q/color 128 64 64))
      (q/line (getx b0) y0 (getx b1) y1)
      (q/stroke (q/color 0 0 128))
      (q/line (getx a0) y0 (getx a1) y1))))

(defn draw-state!
  [{:keys [frame dynamic-state control noise]}]
  (let [lines [(format "Frame %d" frame)
               (format "Position %+.2f Velocity %+.2f" (float (:position dynamic-state)) (float (:velocity dynamic-state)))
               (format "Control %+.2f Noise %+.2f" (float control) (float noise))]]
    (q/text (->> lines
                 (interpose "\n")
                 (apply str))
            margin (- (bottom)
                      (* (+ (q/text-ascent) (q/text-descent))
                         (count lines))))))

(defn ^:dynamic draw!
  []
  ;; update
  (dosync
   (when-not @paused-var
     (step!)))

  ;; draw
  (q/background 255)

  (when @paused-var
    (draw-state! (first @states-var)))
  (draw-control! (current-control))
  (draw-graph! (control-noise-graph))

  (let [pole-type (model-type)]
    (doseq [[theta life] (reverse (ghosts))
            :let [shade (* life 128)]
            :when (< 0 shade)]
      (draw-pole! pole-type (q/color 0 shade) theta))
    (draw-pole! pole-type (q/color 0) (:position (current-state)))))

(defn ^:dynamic key-pressed!
  []
  (condp get (q/raw-key)
    #{\space \p} (dosync (ref-set paused-var (not @paused-var)))
    #{\< \,}     (dosync (when @paused-var (unstep!)))
    #{\> \.}     (dosync (when @paused-var (step!)))
    nil))

;; Applet handling
(defonce applet (atom nil))
(defn set-applet!
  ([] (set-applet! nil))
  ([newapplet]
     (swap! applet
            (fn [olda newa]
              (do
                (when olda (qa/applet-close olda))
                newa))
            newapplet)))

(def stop! set-applet!)
(defn view! []
  (set-applet!
   (qa/applet
    :title "balance"
    :size [900 800]
    :setup setup!
    :draw #(draw!)
    :key-pressed #(key-pressed!))))

;; Startup

(defn -main [& args]
  (view!))
