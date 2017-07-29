import treelearn as tl

tl.run(
    description = "Example program, trains a word autoencoder",

    repositories = {"EGREPO": "/home/douglas/Fun/TreeLearn/example/.git@master"},

    init = tl.command("python3 init.py ${TARGET} --options ${OPTIONS} --seed ${SEED}",
                      chdir = '${EGREPO}',
                      options = {"hidden_scales":   tl.linear(min=0, default=4.0),
                                 "embedding_scale": tl.linear(min=0, default=1.0),
                                 "parameters":      100000}),

    step = tl.command("python3 step.py ${SOURCE} ${TARGET} --options ${OPTIONS} --seed ${SEED}",
                      chdir = '${EGREPO}',
                      options = {"learning_rate": tl.logarithmic(default=0.001),
                                 "algorithm":     tl.either(
                                     {"name": "sgd"},
                                     {"name": "adagrad", "decay": tl.logarithmic(default=0.001)},
                                 )}),

    eval = tl.command("python3 eval.py ${SOURCE}", chdir = '${EGREPO}'),
)
