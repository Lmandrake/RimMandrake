;; Bridge station profile for this project.
;; Data, not code -- Bridge reads it with `read', never `load'.
;;
;; Two panes in one frame, because this project's work splits into two roles that
;; belong side by side. BENCH left, FOUNDRY right.
;;
;; Each pane's colour is exact in Bridge's mode line. Claude's /color gets the
;; nearest of its eight names, so purple stays purple and orange stays orange here
;; -- but note goldenrod and dark orange elsewhere both land on "orange" too, which
;; is the expected loss.

(:bridge-version 1
 :station RIMMASTER
 :split right
 :panes ((:name BENCH   :color "purple" :command claude)
         (:name FOUNDRY :color "orange" :command claude)))
