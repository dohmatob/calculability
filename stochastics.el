;; Synopsis: probabilistic lambda-calculus primitive procedures
;; Author: DOHMATOB Elvis Dopgima <gmdopp@gmail.com>
;; From command-line, run with "emacs --script stochastics.el

;; get cl-lib library from http://elpa.gnu.org/packages/cl-lib-0.4.el
(load "~/.emacs.d/cl-lib/cl-lib.el")
(require 'cl-lib)


(defun rand ()
  "Python-like rand function."
  (cl-random 1.0))


(defun flip (&optional p)
  "Simulates a Bernoulli outcome with parameter p."
  (setq p (if (not p) .5 p))
  (if (> (rand) p) nil t))


(defun bernoulli-sample (n &optional p)
  "Samples n points from a Bernoulli distribution with parameter p."
  (setq samples '())
  (dotimes (i n)
    (setq samples (append samples (list (flip p)))))
  samples)
