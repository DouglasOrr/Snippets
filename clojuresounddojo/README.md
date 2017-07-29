# ClojureSoundDojo

Let's have some fun making sounds (and maybe music?) with functions.

## Usage

Before you start: You'll want [lein](https://raw.github.com/technomancy/leiningen/preview/bin/lein), whatever you're doing, so download it and put it on your path, if you haven't already. Also, it is a good idea to exit any other applications that use sound - as they can interfere with the playback.

Using Emacs, run `lein deps` from the root folder, then (in Emacs) run `M-x clojure-jack-in` or `M-x nrepl-jack-in` as you like. Start off in core.clj, with the basic examples there.

Using Eclipse, make sure that [counterclockwise](http://code.google.com/p/counterclockwise/wiki/Documentation#Install_Counterclockwise_plugin) is installed, and import this folder into your workspace as an existing project. Again, start off in core.clj.

Otherwise, try the following:

    $ lein repl
    => (load-file "src/clojure_sound_dojo/core.clj")
    => (ns clojure-sound-dojo.core)
    => (play (sine 440))
