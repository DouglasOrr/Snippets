(menu-bar-mode -1)
(load-theme 'tango-dark t)
(setq backup-directory-alist
      `((".*" . ,temporary-file-directory)))
(setq auto-save-file-name-transforms
      `((".*" ,temporary-file-directory t)))

(setq-default indent-tabs-mode nil)

(require 'package)
(add-to-list 'package-archives '("melpa" . "http://melpa.org/packages/") t)
(package-initialize)

(require 'flycheck)
(global-flycheck-mode)
(setq flycheck-python-pycompile-executable "python3")
(setq flycheck-python-flake8-executable "flake8")
(setq flycheck-python-pylint-executable "pylint")
