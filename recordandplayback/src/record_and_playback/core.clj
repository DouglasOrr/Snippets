(ns record-and-playback.core)

(defn nano-time
  "Wraps System/nanoTime in a var"
  []
  (System/nanoTime))

(defn sleep
  "Wraps Thread/sleep in a var"
  [t]
  (Thread/sleep t))

(defn- record-execute
  "Execute a function, and record timing info"
  [f & args]
  (let [begin-ns (nano-time)
        result   (apply f args)
        end-ns   (nano-time)]
    {:begin-ns begin-ns
     :end-ns   end-ns
     :args     args
     :result   result}))

(defn- rebind-roots!
  "For each symbol in symbols, rebind it to (vals-fn s)"
  [symbols vals-fn]
  (doseq [s symbols] (.bindRoot (resolve s) (vals-fn s))))

(defn start-recording!
  "Start recording calls made to functions in the given collection of symbols
  returns a new recorder agent"
  [& symbols]
  (let [old-bindings (zipmap symbols (map (comp deref resolve) symbols))
        recording    (atom [])
        begin-ns     (nano-time)]
    (rebind-roots!
     symbols
     (fn [s]
       (let [f (deref (resolve s))]
         (fn [& args]
           (let [{result :result :as record}
                 (apply record-execute f args)]
             (swap! recording conj (assoc record :symbol s))
             result)))))
    {:begin-ns     begin-ns
     :old-bindings old-bindings
     :recording    recording}))

(defn stop-recording!
  "Stop recording calls, and return a 'recording' of the events"
  [{begin-ns     :begin-ns
    recording    :recording
    old-bindings :old-bindings}]
  (let [_               (rebind-roots! (keys old-bindings) old-bindings)
        final-recording @recording
        end-ns          (nano-time)]
    {:begin-ns  begin-ns
     :end-ns    end-ns
     :recording final-recording}))

(defn playback!
  "Playback a recording in a given mode (:timed or :sequential)
  N.B. 'timed' mode just uses the rough Thread/sleep function to do timing"
  [mode {start-time :begin-ns
         stop-time  :end-ns
         recording  :recording}]
  (let [playback-start (nano-time)
        sleep-to       (fn [time]
                         (sleep
                          (max 0 (/ (- (- time start-time)
                                       (- (nano-time) playback-start))
                                    1000000))))]
    (doseq [{symbol :symbol time :begin-ns args :args} recording]
      (when (= :timed mode) (sleep-to time))
      (apply (deref (resolve symbol)) args))
    (when (= :timed mode) (sleep-to stop-time))))

(defmacro with-recording!
  "Record a sequence of actions on the provided vector of symbols,
  returning a pair [result recording]
  e.g. (with-recording! [println pprint] (println :A))"
  [symbols expr]
  (let [quoted-symbols (map (partial list 'quote) symbols)]
    `(let [recorder# (start-recording! ~@quoted-symbols)]
       (try
         (let [result#    ~expr
               recording# (stop-recording! recorder#)]
           [result# recording#])
         (finally (stop-recording! recorder#))))))

(comment
  (defn play-note [x] (println "Playing" x) x)
  )
