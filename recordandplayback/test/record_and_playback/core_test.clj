(ns record-and-playback.core-test
  (:use midje.sweet
        record-and-playback.core))

(fact "start-recording! <work> stop-recording! works"
      (let [rec (start-recording! 'println 'print)
            _   (println "one")
            _   (print "two" "three")]
        (stop-recording! rec))
      => {:begin-ns :nA
          :end-ns   :nZ
          :recording [{:symbol   'println
                       :begin-ns :n1a
                       :end-ns   :n1b
                       :args     ["one"]
                       :result   nil
                       }
                      {:symbol   'print
                       :begin-ns :n2a
                       :end-ns   :n2b
                       :args     ["two" "three"]
                       :result   nil
                       }]
          }
      (provided (nano-time) =streams=> [:nA :n1a :n1b :n2a :n2b :nZ]))

(defn failfn [& args] (throw (Exception. (str "Called with " args))))

(fact "with-recording, playback (sequential) works"
      (->> (with-recording! [failfn]
             (do
               (failfn "one")
               (failfn "two" "three")))
           second
           (playback! :sequential))
      => anything
      (provided (failfn "one")         => nil :times 2
                (failfn "two" "three") => nil :times 2
                (sleep anything)       => nil :times 0))

(fact "with-recording, playback (timed) works"
      (->> (with-recording! [failfn]
             (do
               (failfn "one")
               (failfn "two" "three")))
           second
           (playback! :timed))
      => anything
      (provided
       (nano-time)    =streams=> (map (partial * 1000000)
                                      [20  ; begin (all)        t=0
                                       30  ; begin (one)        t=10
                                       0   ; end   (one)
                                       50  ; begin (two three)  t=30
                                       0   ; end   (two three)
                                       100 ; end   (all)        t=80
                                       100 ; end   ('finally')
                                        ; --- playback ---
                                       200 ; playback-start     t=0
                                       205 ; before (one)       t=5
                                       228 ; before (two three) t=28
                                       280 ; before (end)       t=80
                                       ])
       (sleep 5) => nil :times 1
       (sleep 2) => nil :times 1
       (sleep 0) => nil :times 1
       (failfn "one")         => nil :times 2
       (failfn "two" "three") => nil :times 2))
