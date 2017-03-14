
(define (problem generic)
  (:domain western-duel)
  (:objects gunman - char)
  (:init (alive gunman))
  (:goal (and (not (alive gunman))))
)