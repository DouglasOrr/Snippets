;; General settings

(menu-bar-mode -1)
(load-theme 'tango-dark t)
(setq backup-directory-alist `((".*" . ,temporary-file-directory)))
(setq auto-save-file-name-transforms `((".*" ,temporary-file-directory t)))

(setq-default indent-tabs-mode nil)
(setq-default c-basic-offset 4)
(setq-default tab-width 4)

(c-add-style "doug-style"
             '("stroustrup"
               (c-offsets-alist . ((arglist-close . 0)))))
(setq-default c-default-style "doug-style")

(add-hook 'after-init-hook #'global-flycheck-mode)

;; Packages

(require 'package)
(add-to-list 'package-archives '("melpa" . "http://melpa.org/packages/") t)
(package-initialize)

;; Auto

(custom-set-variables
 ;; custom-set-variables was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(package-selected-packages
   (quote
    (clojure-mode haskell-mode rust-mode scala-mode flycheck-pyflakes ninja-mode python-black dockerfile-mode yaml-mode markdown-mode))))
(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 )
