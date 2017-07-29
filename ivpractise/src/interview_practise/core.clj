(ns interview-practise.core
  (:require [clojure.string :as str]
            [clojure.java.io :as io]))

;; Core instructions

(def white \O)

(defn create
  "Create a M x N image (M is the width, N the height).
  The image is stored as a vector-of-vectors, row-major."
  [m n]
  (vec (repeat n (vec (repeat m white)))))

(defn show
  "Create a string representation of the image."
  [img]
  (str/join "\n"
            (map (partial str/join "") img)))

(defn clear
  "Clear the given image to white (O)"
  [img]
  (mapv (partial mapv (constantly white)) img))

(defn set-pixel
  "Set a single pixel to a given color"
  [img col row colour]
  (assoc-in img [row col] colour))

(defn draw-vline
  "Draw a vertical line of the given dimensions.
  The range [min-row max-row] is inclusive."
  [img col [min-row max-row] colour]
  (let [img-head (take (inc max-row))])
  (vec (concat (take min-row img)
               (->> img
                    (take (inc max-row))
                    (drop min-row)
                    (map (fn [rowv] (assoc rowv col colour))))
               (drop (inc max-row) img))))

(defn draw-hline
  "Draw a horizontal line of the given dimensions.
  The range [min-col max-col] is inclusive."
  [img [min-col max-col] row colour]
  (update img row
          (fn [rowv]
            (vec (concat (take min-col rowv)
                         (repeat (inc (- max-col min-col)) colour)
                         (drop (inc max-col) rowv))))))

(defn neighbours
  "Get a sequence of neighbours of the given pixel."
  [img col row]
  (remove nil?
          [(when (< 0 col) [(dec col) row])
           (when (< 0 row) [col (dec row)])
           (when (< col (dec (count (img 0)))) [(inc col) row])
           (when (< row (dec (count img))) [col (inc row)])]))

(defn adjacents
  "Get a set of all the adjacent (in the flood-fill sense) pixels
  of the given pixel."
  ([img col row] (adjacents img col row #{}))
  ([img col row visited]
   (let [current-colour (get-in img [row col])]
     (reduce (fn [visited [n-col n-row]]
               (if (and (= current-colour (get-in img [n-row n-col]))
                        (not (visited [n-col n-row])))
                 (adjacents img n-col n-row visited)
                 visited))
             (conj visited [col row])
             (neighbours img col row)))))

(defn flood-fill
  "Flood fill an image using adjacent pixel colours
  from a starting point."
  ([img col row colour]
   (let [fill? (adjacents img col row)]
     (->> img
          (map-indexed
           (fn [i-row rowv]
             (->> rowv
                  (map-indexed (fn [i-col old-colour]
                                 (if (fill? [i-col i-row])
                                   colour
                                   old-colour)))
                  vec)))
          vec))))

;; Editor

(defn -handle-line
  "Handle a single input command"
  [img line]
  (let [[cmd & args] (str/split line #" ")
        args (vec args)
        co #(dec (Integer/parseInt %))]
    (case cmd
      "I" (create (Integer/parseInt (args 0)) (Integer/parseInt (args 1)))
      "C" (clear img)
      "L" (set-pixel img (co (args 0)) (co (args 1)) (nth (args 2) 0))
      "V" (draw-vline img (co (args 0)) [(co (args 1)) (co (args 2))] (nth (args 3) 0))
      "H" (draw-hline img [(co (args 0)) (co (args 1))] (co (args 2)) (nth (args 3) 0))
      "F" (flood-fill img (co (args 0)) (co (args 1)) (nth (args 2) 0))
      "S" (do (println (show img))
              img)
      "X" (System/exit 0))))

(defn -main
  "Run the 'interactive editor'."
  []
  (doall
    (reduce -handle-line
            nil
            (line-seq (io/reader System/in)))))
