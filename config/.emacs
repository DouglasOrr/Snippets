(menu-bar-mode -1)
(load-theme 'tango-dark t)
(setq backup-directory-alist
      `((".*" . ,temporary-file-directory)))
(setq auto-save-file-name-transforms
      `((".*" ,temporary-file-directory t)))

(setq-default indent-tabs-mode nil)
(setq-default c-basic-offset 4)
(setq-default tab-width 4)

(require 'package)
(add-to-list 'package-archives '("melpa" . "http://melpa.org/packages/") t)
(package-initialize)

(require 'flycheck)
(global-flycheck-mode)
(setq flycheck-python-pycompile-executable "python3")
(setq flycheck-python-flake8-executable "flake8")
(setq flycheck-python-pylint-executable "pylint")

;; Custom C++ mode
(c-add-style "doug-style"
	     '("stroustrup"
	       (indent-tabs-mode . nil)        ; use spaces rather than tabs
	       (c-basic-offset . 2)            ; indent by two spaces
	       (c-offsets-alist . ((inline-open . 0)  ; custom indentation rules
				   (brace-list-open . 0)
				   (statement-case-open . +)))))
(defun my-c++-mode-hook () (c-set-style "doug-style"))
(add-hook 'c++-mode-hook 'my-c++-mode-hook)
