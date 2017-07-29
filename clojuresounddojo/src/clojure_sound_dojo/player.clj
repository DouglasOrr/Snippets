(ns clojure-sound-dojo.player
  (:import  [java.nio ByteBuffer ByteOrder]
            [javax.sound.sampled AudioSystem AudioFormat AudioFormat$Encoding LineListener])
  (:require [clojure.java.io :as io]))

;; Mirky details, keep scrolling

(defn audio-format
  "Return an audio format object with the given properties (default: CD stereo)"
  [& {:keys [sample-rate sample-size-bits channels signed? big-endian?]
      :or   {sample-rate      44100
             sample-size-bits 16
             channels         2
             signed?          true
             big-endian?      false}}]
  (AudioFormat. (float sample-rate)
                (int sample-size-bits)
                (int channels)
                (boolean signed?)
                (boolean big-endian?)))

(defn encode
  "Encode a sequence of samples using the specified SampleFormat"
  [sformat samples]
  (let [_             (assert (= AudioFormat$Encoding/PCM_SIGNED (.getEncoding sformat))
                              "Unsigned sample encodings are not supported")
        write-channel (condp = (/ (.getSampleSizeInBits sformat) 8)
                        1 (fn [^ByteBuffer b c] (.put      b (byte  (* Byte/MAX_VALUE    c))))
                        2 (fn [^ByteBuffer b c] (.putShort b (short (* Short/MAX_VALUE   c))))
                        4 (fn [^ByteBuffer b c] (.putInt   b (int   (* Integer/MAX_VALUE c))))
                        (assert false "Bad sample size"))
        write-sample  (if (= 1 (.getChannels sformat))
                        (fn [b c]                        (write-channel b c))
                        (fn [b sample] (doseq [c sample] (write-channel b c))))]

    (let [b (ByteBuffer/allocate (* (.getFrameSize sformat) (count samples)))]
      (.order b (if (.isBigEndian sformat)
                  ByteOrder/BIG_ENDIAN
                  ByteOrder/LITTLE_ENDIAN))
      (doseq [s samples] (write-sample b s))
      (.array b))))

(defn- riff-chunk
  [sformat remaining-size]
  (.array (doto (ByteBuffer/allocate 12)
            (.order  ByteOrder/LITTLE_ENDIAN)
            (.put    (.getBytes "RIFF"))
            (.putInt (+ 4 remaining-size))
            (.put    (.getBytes "WAVE")))))

(defn- fmt-chunk
  [sformat]
  (.array (doto (ByteBuffer/allocate 24)
            (.order    ByteOrder/LITTLE_ENDIAN)
            (.put      (.getBytes "fmt "))
            (.putInt   16) ; Chunk data size
            (.putShort 1)  ; PCM/uncompressed
            (.putShort (.getChannels sformat))
            (.putInt   (int (.getSampleRate sformat)))
            (.putInt   (int (* (.getSampleRate sformat) (.getFrameSize sformat))))
            (.putShort (.getFrameSize sformat))
            (.putShort (.getSampleSizeInBits sformat)))))

(defn- data-chunk-header
  [sformat data-size]
  (.array (doto (ByteBuffer/allocate 8)
            (.order  ByteOrder/LITTLE_ENDIAN)
            (.put    (.getBytes "data"))
            (.putInt data-size))))

;; Samples API

(defn sample
  "Samples a function at fixed intervals, returning {:samples x :rate r}"
  ([waveform] (sample [0 1] waveform))
  ([[start end] waveform & {:keys [rate] :or {rate 44100}}]
     (let [delta   (float (/ rate))
           samples (->> (iterate (partial + delta) start)
                        (take (* rate (- end start)))
                        (map waveform))]
       {:samples samples
        :rate    rate})))

(defn save-wav-samples
  "Save a sequence of samples as a WAVE file"
  [filename {:keys [samples rate]}]
  (let [sformat     (audio-format
                     :sample-rate      rate
                     :sample-size-bits 16
                     :channels         (if (sequential? (first samples))
                                         (count (first samples)) 1)
                     :signed?          true
                     :big-endian?      false)
        data        (encode sformat samples)
        data-header (data-chunk-header sformat (count data))
        fmt         (fmt-chunk sformat)
        riff        (riff-chunk sformat (+ (count fmt) (count data-header) (count data)))]
    (with-open [w (io/output-stream filename)]
      (.write w riff)
      (.write w fmt)
      (.write w data-header)
      (.write w data))))

(defn play-samples
  "Play a sequence of samples (float values between -1 and 1, or stereo pairs of samples)
  at the provided rate"
  [{:keys [samples rate]}]
  (let [sformat (audio-format
                 :sample-rate      rate
                 :sample-size-bits 16
                 :channels         (if (sequential? (first samples))
                                     (count (first samples)) 1)
                 :signed?          true
                 :big-endian?      false)]

    (with-open [line (AudioSystem/getSourceDataLine sformat)]
      (.open line sformat)
      (.start line)
      (doseq [section (partition-all
                       (/ (.getBufferSize line) (.getFrameSize sformat) 2)
                       samples)
              :let [encoded (encode sformat section)]]
        (.write line encoded 0 (count encoded)))
      (.stop line))))

;; Simple API

(defn save
  "Sample, then save a function waveform (default: 1s from t=0)
  a 'waveform' is a function from time to amplitude,
  returning a single float in range [-1 1] (mono), or a pair of floats (stereo)"
  ([filename waveform] (save filename [0 1] waveform))
  ([filename [start end] waveform & {:keys [rate] :or {rate 44100}}]
     (save-wav-samples filename (sample [start end] waveform :rate rate))))

(defn play
  "Sample, then play a function waveform (default: 1s from t=0)
  a 'waveform' is a function from time to amplitude,
  returning a single float in range [-1 1] (mono), or a pair of floats (stereo)"
  ([waveform] (play [0 1] waveform))
  ([[start end] waveform & {:keys [rate] :or {rate 44100}}]
     (play-samples (sample [start end] waveform :rate rate))))
