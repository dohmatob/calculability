;; Synopsis: probabilistic lambda-calculus primitive procedures
;; Author: DOHMATOB Elvis Dopgima <gmdopp@gmail.com>
;; From command-line, run with "emacs --script stochastics.el

;; get cl-lib library from http://elpa.gnu.org/packages/cl-lib-0.4.el
(load "~/.emacs.d/cl-lib/cl-lib.el")
(require 'cl-lib)

(defun rand ()
  "Python-like rand function."
  (cl-random 1.0))

(defun flip (p)
  "Simulates a Bernoulli outcome with parameter p."
  (if (> (rand) p) nil t))

(defun medical-diagnosis-core (lung-cancer TB cold stomach-flu other)
  "Generate symptoms from signs. Curtesy of the Church tutorial at "
  "http://projects.csail.mit.edu/church/wiki/Generative_Models. "
  "Translated to Emacs Lisp by me [Elvis]"
  (progn
    (setq lung-cancer (flip lung-cancer))
    (setq TB (flip TB))
    (setq cold (flip cold))
    (setq stomach-flu (flip stomach-flu))
    (setq other (flip other))
    
    (setq cough (or (and cold (flip 0.5))
		    (and lung-cancer (flip 0.3))
		    (and TB (flip 0.7))
		    (and other (flip 0.01))))
    
    (setq fever (or (and cold (flip 0.3))
		    (and stomach-flu (flip 0.5))
		    (and TB (flip 0.1))
		    (and other (flip 0.01))))
    
    (setq chest-pain (or (and lung-cancer (flip 0.5))
			 (and TB (flip 0.5))
			 (and other (flip 0.01))))
    
    (setq shortness-of-breath (or (and lung-cancer (flip 0.5))
				  (and TB (flip 0.2))
				  (and other (flip 0.01))))

    (list (list "cough" cough) (list "fevel" fever) (list "chest-pain" chest-pain) (list "shortness-of-breath" shortness-of-breath))))

(defun medical-diagnosis-normal ()
  "Rather well."
  (message "Well patient status:")
  (progn
    (setq status (medical-diagnosis-core 0.01 0.005 0.2 0.1 0.1))
    (message (format "Normal patient status: %s" status))
    status))

(defun medical-diagnosis-sick ()
  "This guy is thoroughly ill."
  (progn
    (setq status (medical-diagnosis-core 0.6 0.7 0.8 0.9 1))
    (message (format "Sick patient status: %s" status))
    status))

(medical-diagnosis-normal)
(medical-diagnosis-sick)
