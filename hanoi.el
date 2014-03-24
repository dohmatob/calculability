;; From command-line run with "emacs --script hanoi.el"

(defun hanoi-core (n a b c mvcnt)
  "Simplest possible towers-of-hanoi solver. NB.:- Can be done iteratively too."
  (if (> n 0)
      (if (< n 2)
	  (progn
	    (setq mvcnt (+ mvcnt 1))
	    (message (format "[%d] Move topmost disk from %s to %s" mvcnt a c))
	    mvcnt)
	(progn
	  (setq mvcnt (hanoi-core (- n 1) a c b mvcnt))
	  (setq mvcnt (hanoi-core 1 a b c mvcnt))
	  (setq mvcnt (hanoi-core (- n 1) b a c mvcnt))
	  mvcnt))
    nil))

(defun hanoi (n a b c)
  "Wrapper."
  (hanoi-core n a b c 0)
  (message "Done."))

(hanoi 15 "A" "B" "C")