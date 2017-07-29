(ns clojure-sound-dojo.player-test
  (:require [clojure-sound-dojo.player :refer :all]
            [midje.sweet :refer :all]
            [clojure.java.io :as io])
  (:import  javax.sound.sampled.AudioFormat$Encoding
            java.io.ByteArrayOutputStream))

(fact "sample works"
      (sample [2 2.45] - :rate 10)
      => (just {:rate 10
                :samples (just (map roughly [-2 -2.1 -2.2 -2.3 -2.4]))}))

(fact "audio-format returns CD format by default"
      (let [a (audio-format)]
        (.getChannels a)         => 2
        (.getEncoding a)         => AudioFormat$Encoding/PCM_SIGNED
        (.getFrameRate a)        => (roughly 44100.0)
        (.getFrameSize a)        => 4
        (.getSampleRate a)       => (roughly 44100.0)
        (.getSampleSizeInBits a) => 16
        (.isBigEndian a)         => false))

(fact "encode works"
      (seq (encode (audio-format :big-endian? true :sample-size-bits 16 :channels 2)
                   [[0.0 1.0] [1.0 1.0] [0.0 -1.0] [-1.0 -1.0]]))
      => (map unchecked-byte
              [0x00 0x00  0x7f 0xff
               0x7f 0xff  0x7f 0xff
               0x00 0x00  0x80 0x01
               0x80 0x01  0x80 0x01])
      (seq (encode (audio-format :big-endian? false :sample-size-bits 8 :channels 1)
                   [0.0 0.5 1.0]))
      => (map unchecked-byte
              [0x00 0x3f 0x7f]))

(fact "save-wav-samples works"
      (let [output (ByteArrayOutputStream.)]
        (save-wav-samples "in-memory.wav" {:rate 44100
                                           :samples [[0 1] ..more..]}) => nil
        (provided (io/output-stream "in-memory.wav") => output
                  (encode anything [[0 1] ..more..])
                  => (byte-array (map unchecked-byte [0x12 0x34 0x56 0x78])))
        (seq (.toByteArray output))
        => (map unchecked-byte [0x52 0x49  0x46 0x46  ; "RIFF"
                                0x28 0x00  0x00 0x00  ; riff-length:40
                                0x57 0x41  0x56 0x45  ; "WAVE"

                                0x66 0x6d  0x74 0x20  ; "fmt "
                                0x10 0x00  0x00 0x00  ; fmt-length
                                0x01 0x00  0x02 0x00  ; compression-code:1, n-channels:2
                                0x44 0xac  0x00 0x00  ; sample-rate:44100
                                0x10 0xb1  0x02 0x00  ; bytes-per-second:176400
                                0x04 0x00  0x10 0x00  ; block-align:4, bits-per-sample:16

                                0x64 0x61  0x74 0x61  ; "data"
                                0x04 0x00  0x00 0x00  ; data-length
                                0x12 0x34  0x56 0x78  ; payload
                                ])))
