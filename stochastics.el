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

(defun medical-diagnosis-core (lc tb c sf o)
  "Generate symptoms from signs. Curtesy of the Church tutorial at "
  "http://projects.csail.mit.edu/church/wiki/Generative_Models. "
  "Translated to Emacs Lisp by me [Elvis]"
  (progn
    (defvar lung-cancer (flip lc))
    (defvar TB (flip tb))
    (defvar cold (flip c))
    (defvar stomach-flu (flip sf))
    (defvar other (flip o))
    
    (defvar cough (or (and cold (flip 0.5))
		    (and lung-cancer (flip 0.3))
		    (and TB (flip 0.7))
		    (and other (flip 0.01))))
    
    (defvar fever (or (and cold (flip 0.3))
		    (and stomach-flu (flip 0.5))
		    (and TB (flip 0.1))
		    (and other (flip 0.01))))
    
    (defvar chest-pain (or (and lung-cancer (flip 0.5))
			 (and TB (flip 0.5))
			 (and other (flip 0.01))))
    
    (defvar shortness-of-breath (or (and lung-cancer (flip 0.5))
				  (and TB (flip 0.2))
				  (and other (flip 0.01))))

    (list (list "cough" cough) (list "fevel" fever) (list "chest-pain" chest-pain) (list "shortness-of-breath" shortness-of-breath))))

(defun medical-diagnosis-normal ()
  "Rather well."
  (message "Well patient status:")
  (progn
    (defvar status (medical-diagnosis-core 0.01 0.005 0.2 0.1 0.1))
    (message (format "Normal patient status: %s" status))
    status))

(defun medical-diagnosis-sick ()
  "This guy is thoroughly ill."
  (progn
    (defvar status (medical-diagnosis-core 0.6 0.7 0.8 0.9 1))
    (message (format "Sick patient status: %s" status))
    status))

(medical-diagnosis-normal)
(medical-diagnosis-sick)

(byte-compile-file "hanoi.el")