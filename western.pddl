(define (domain western-duel)
  (:requirements)
  (:types element char place item - object
		  observer bartender sheriff - char
		  bar - place
		  container - item
		  door - container
		  weapon - item
		  gun ammo tnt - weapon
          horse bottle cig - item
		  step literal - element
		  )
  (:predicates 	   
			   (has ?c - char ?it - item)
			   (at ?object - object ?place - place)
			   (= ?obj - object ?obj2 - object)
			   (adj ?p1 - place ?p2 - place)
			   (is ?literal - literal)
			   (occurs ?step - step)
			   
			   ;guns
			   (loaded ?g - gun)
			   (loaded-with ?gun - gun ?ammo - ammo)
			   (shot-at ?gun - gun ?target - object)
			   (aimed-at ?g - gun ?target - object)
			   (holstered ?g - gun)
			   (cocked ?g - gun)
			   (raised ?g - gun)
			   (marksman ?c - char)
			   (hit-by-bullet ?ob - object)
			   (arrested ?c - char)
			   
			   ;cognitive
			   (stare-at ?c - char ?ob - object)
			   (sees ?c - char ?it - item)
			   (facing ?c - char ?targ - object)
			   (looking ?c - char ?targ - object)
			   (staring ?c - char ?c2 - char)
			   (provoked ?c - char)
			   (bel-char ?c - char ?info - literal)
			   (allies ?c1 - char ?c2 - char)
			   (intends ?c - char ?goal - literal)
			   
			   ;physical states
			   (alive ?char - char)
			   (standing ?c1 - char)
			   (on-ground ?c - char)
			   (squared-off ?c - char ?c2 - char)
			   (tied-up ?c - char)
			   (drunk ?c - char)
			   
			   ;item specific
			   (opened ?container - container)
			   (closed ?container - container)
			   (on-horse ?c - char ?h - horse)
			   (smoking ?c - char)
			   (drinking ?c - char)
			   )
			   
  (:action leave
	:parameters (?person - char ?p - place)
	:precondition (and (alive ?person) (at ?person ?p))
	:effect (not (at ?person ?p))
	:agents (?person))
	
  (:action arrive
	:parameters (?person - char ?p - place)
	:precondition (and (alive ?person))
	:effect (at ?person ?p)
	:agents (?person))

  (:action run
    :parameters (?person - char ?from - place ?to - place)
    :precondition(and (at ?person ?from) (alive ?person))
    :effect (and (not (at ?person ?from)) (at ?person ?to))
    :agents (?person))

  (:action arrest
	:parameters (?sheriff - sheriff ?c - char ?p - place)
	:precondition (and (at ?sheriff ?p) (at ?c ?p) (alive ?sheriff) (alive ?c))
	:effect (and (arrested ?c))
	:agents (?sheriff))
			   
  (:action stare-at
	:parameters (?looker - char ?lookee - char ?loc - place)
	:precondition(and
					(at ?looker ?loc)
					(at ?lookee ?loc)
					(facing ?looker ?lookee)
					(looking ?looker ?lookee)
					(alive ?looker)
					)
	:effect (and (staring ?looker ?lookee))
	:agents (?looker))
	
  (:action look-at
	:parameters (?looker - char ?lookee - char ?loc - place)
	:precondition(and
					(at ?looker ?loc)
					(at ?lookee ?loc)
					(facing ?looker ?lookee)
					(alive ?looker)
					)
	:effect (and (looking ?looker ?lookee))
	:agents (?looker))

  (:action look-from-to
    :parameters (?looker - char ?former-targ - object ?new-targ - object ?p - place)
    :precondition (and (at ?looker ?p) (at ?former-targ ?p) (at ?new-targ ?p) (alive ?looker)
        (looking ?looker ?former-targ))
    :effect (and (looking ?looker ?new-targ) (not (looking ?looker ?former-targ)))
    :agents (?looker))
	
  (:action carry-from-to
	:parameters (?carrier - char ?item - item ?p1 - place ?p2 - place)
	:precondition (and (alive ?carrier) (at ?carrier ?p1) (at ?item ?p1))
	:effect (and (at ?carrier ?p2) (not (at ?carrier ?p1)) (at ?item ?p2) (not (at ?item ?p1)))
	:agents (?carrier))
	
  (:action face-at
	:parameters (?facer - char ?facee - object)
	:precondition(alive ?facer)
	:effect (and (facing ?facer ?facee))
	:agents (?facer))
	
  (:action face-from-to
	:parameters (?facer - char ?former-targ - object ?new-targ - object)
	:precondition(and (alive ?facer) (facing ?facer ?former-targ))
	:effect (and (facing ?facer ?new-targ) (not (facing ?facer ?former-targ)))
	:agents (?facer))
	
  (:action draw-gun
	:parameters (?drawer - char ?gun - gun)
	:precondition (and (has ?drawer ?gun) (holstered ?gun))
	:effect (and (not (holstered ?gun)) (raised ?gun))
	:agents (?drawer))
	
  (:action raise-gun
	:parameters (?c - char ?g - gun)
	:precondition (and (has ?c ?g) (alive ?c) (not (holstered ?g)))
	:effect (and (raised ?g))
	:agents (?c))
	
  (:action load-gun
	:parameters (?c - char ?g - gun ?a - ammo)
	:precondition (and (has ?c ?g) (has ?c ?a) (alive ?c))
	:effect (and (loaded ?g) (not (has ?c ?a)))
	:agents (?c))
	
  (:action get-shot
	:parameters (?victim - char ?gun - gun)
	:precondition (and (shot-at ?gun ?victim))
	:effect (and (hit-by-bullet ?victim))
	:agents ())
	
  (:action fall
	:parameters (?faller - char)
	:precondition (and (hit-by-bullet ?faller))
	:effect (and (on-ground ?faller))
	:agents()
  )
  
  (:action die
	:parameters (?victim - char)
	:precondition (hit-by-bullet ?victim)
	:effect (not (alive ?victim))
	:agents()
  )
  
  (:action walk
	:parameters (?walker - char ?from - place ?to - place)
	:precondition (and (at ?walker ?from) (adj ?from ?to) (not (on-ground ?walker)) (alive ?walker))
	:effect (and (at ?walker ?to))
	:agents (?walker))
	
  (:action mount
	:parameters (?rider - char ?horse - horse ?p - place)
	:precondition (and (alive ?rider) (at ?rider ?p) (at ?horse ?p))
	:effect (on-horse ?rider ?horse)
	:agents (?rider))
	
  (:action dismount
	:parameters (?rider - char ?horse - horse)
	:precondition (and (alive ?rider) (on-horse ?rider ?horse))
	:effect (and (not (on-horse ?rider ?horse)))
	:agents (?rider))
	
  (:action ride
	:parameters (?rider - char ?horse - horse ?from - place ?to - place)
	:precondition (and (on-horse ?rider ?horse) (at ?rider ?from))
	:effect (and (at ?rider ?to) (at ?horse ?to))
	:agents (?rider))
	
  (:action reveal
	:parameters (?revealer - char ?looker - char ?info - literal)
	:precondition (and (is ?info) (alive ?revealer) (alive ?looker) (looking ?looker ?revealer))
	:effect (and (bel-char ?looker ?info))
	:agents (?revealer))
	

  (:action fire-gun
	:parameters (?cowboy - char ?target - object ?gun - gun ?ammo - ammo ?loc - place)
	:precondition(and (has ?cowboy ?gun)
					  (at ?cowboy ?loc)
					  (at ?target ?loc)
					  (raised ?gun)
					  (cocked ?gun)
					  (aimed-at ?gun ?target)
					  (loaded-with ?gun ?ammo)
					  (alive ?cowboy)
					  )
	:effect (and 
				(shot-at ?gun ?target))
	:agents (?cowboy))
	
  (:action square-off
	:parameters(?cowboy1 - char ?cowboy2 - char ?gun1 - gun ?gun2 - gun ?loc - place)
	:precondition(and (has ?cowboy1 ?gun1)
					  (has ?cowboy2 ?gun2)
					  (alive ?cowboy1)
					  (alive ?cowboy2)
					  (at ?cowboy1 ?loc)
					  (at ?cowboy2 ?loc)
					  (staring ?cowboy1 ?cowboy2)
					  (staring ?cowboy2 ?cowboy1)
					  (holstered ?gun1)
					  (holstered ?gun2)
					)
	:effect (squared-off ?cowboy1 ?cowboy2)
	:agents (?cowboy1 ?cowboy2)
  )
  
  (:action provoke
	:parameters (?provoker - char ?provokee - char ?loc - place)
	:precondition (and  (at ?provoker ?loc) 
						(at ?provokee ?loc) 
						(alive ?provoker) 
						(alive ?provokee) 
						(not (squared-off ?provoker ?provokee)))
	:effect (provoked ?provokee)
	:agents (?provoker))
	
  (:action adjust-clothing
	:parameters (?adjuster - char)
	:precondition (alive ?adjuster)
	:effect ()
	:agents (?adjuster))

  (:action holster-gun
	:parameters (?gunman - char ?gun - gun)
	:precondition (and (has ?gunman ?gun) (alive ?gunman) (not (holstered ?gun)))
	:effect (holstered ?gun)
	:agents (?gunman))
	
  (:action taunt
	:parameters (?gunman1 - char ?gunman2 - char)
	:precondition(and (squared-off ?gunman1 ?gunman2) (alive ?gunman1) (alive ?gunman2))
	:effect (provoked ?gunman2)
	:agents (?gunman1)
  )
  
  (:action side-step
	:parameters (?side-stepper - char)
	:precondition (alive ?side-stepper)
	:effect ()
	:agents (?side-stepper))
	
  (:action smokes
	:parameters (?smoker - char ?cig - cig)
	:precondition(and (alive ?smoker) (has ?smoker ?cig))
	:effect (smoking ?smoker)
	:agents (?smoker))
	
  (:action drinks
	:parameters (?drinker - char ?bottle - bottle)
	:precondition (and (alive ?drinker) (has ?drinker ?bottle))
	:effect (drinking ?drinker)
	:agents (?drinker))

  (:action drink-with
	:parameters (?drinker - char ?other - char ?p - place)
	:precondition(and (alive ?drinker) (alive ?other) (drinking ?drinker) (at ?drinker ?p) (at ?other ?p))
	:effect (bel-char ?other (drunk ?drinker))
	:agents(?drinker))
  
  (:action assent
	:parameters (?ger - char ?gee - char ?loc - place)
	:precondition (and  (alive ?ger) (provoked ?ger) (provoked ?gee)
						(alive ?gee) 
						(at ?ger ?loc) 
						(at ?gee ?loc))
	:effect (and    (intends ?ger (squared-off ?ger ?gee))
					(intends ?gee (squared-off ?ger ?gee))))

  (:action de-escalate
	:parameters (?c1 - char ?c2 - char)
	:precondition (and (alive ?c1) (alive ?c2) (squared-off ?c1 ?c2))
	:effect ()
	:agents(?c1))

  (:action open
	:parameters (?c1 - char ?d - container ?p1 - place)
	:precondition (and (alive ?c1) (at ?c1 ?p1) (at ?d ?p1) (not (opened ?d)))
	:effect (opened ?d)
	:agents (?c1))
	
  (:action cheer
	:parameters (?c1 - char)
	:precondition (alive ?c1)
	:effect ()
	:agents (?c1))
	
  (:action close
	:parameters (?c1 - char ?d - container ?p1 - place)
	:precondition (and (alive ?c1) (at ?c1 ?p1) (at ?d ?p1) (opened ?d))
	:effect (closed ?d)
	:agents (?c1))
	
  (:action fall-from-to
	:parameters (?faller - char ?from - place ?to - place)
	:precondition (at ?faller ?from)
	:effect (and (at ?faller ?to) (not (at ?faller ?from)) (on-ground ?faller))
	:agents())
	
  (:action ask-for
	:parameters (?asker - char ?haser - char ?item - item ?p - place)
	:precondition (and (alive ?asker) (alive ?haser) (has ?haser ?item)
		(at ?haser ?p) (at ?asker ?p) (allies ?asker ?haser))
	:effect (intends ?haser (has ?asker ?item))
	:agents (?asker))
	
  (:action identify
	:parameters (?identifier - char ?recipient - char ?p - place)
	:precondition (and (alive ?identifier) (at ?identifier ?p) (alive ?recipient) (at ?recipient ?p))
	:effect (bel-char ?identifier (at ?recipient ?p))
	:agents (?identifier))
	
  (:action give
	:parameters (?giver - char ?taker - char ?item - item ?p - place)
	:precondition (and (alive ?giver) (alive ?taker) (has ?giver ?item)
		(at ?giver ?p) (at ?taker ?p))
	:effect (and (has ?taker ?item) (not (has ?giver ?item)))
	:agents (?giver ?taker)
	)
	
  (:action take-gun
	:parameters (?taker - char ?gun - gun ?takee - char ?p - place)
	:precondition(and (alive ?taker) (has ?takee ?gun) (at ?taker ?p) (at ?takee ?P))
	:effect (and (has ?taker ?gun) (not (has ?takee ?gun)))
	:agents (?taker))

  (:action aim-gun 
	:parameters (?c1 - char ?t - object ?p - place ?g - gun)
	:precondition(and (alive ?c1) (at ?c1 ?p) (at ?t ?p) (has ?c1 ?g) (not (holstered ?g)))
	:effect (and (raised ?g) (aimed-at ?g ?t))
	:agents (?c1))

  (:action stand-up
	:parameters (?c1 - char)
	:precondition (and (alive ?c1) (not (standing ?c1)))
	:effect (and (standing ?c1) (not (on-ground ?c1)))
	:agents(?c1))
	
  (:action lower-gun
	:parameters (?c1 - char ?g - gun)
	:precondition (and (has ?c1 ?g) (raised ?g))
	:effect (not (raised ?g))
	:agents (?c1))
	
  (:action drop-gun
	:parameters (?c1 - char ?g - gun ?p - place)
	:precondition(and (has ?c1 ?g) (at ?c1 ?p) (not (holstered ?g)))
	:effect (and (not (has ?c1 ?g)) (at ?g ?p))
	:agents (?c1))
	
 ; drop item, can't drop a horse though, which always has a location
  (:action drop
	:parameters (?c1 - char ?g - item ?p - place)
	:precondition(and (has ?c1 ?g) (at ?c1 ?p) (not (at ?g ?p))) 
	:effect (and (not (has ?c1 ?g)) (at ?g ?p))
	:agents (?c1))

  (:action pick-up
    :parameters (?c - char ?thing - item ?p - place)
    :precondition (and (alive ?c) (at ?thing ?p) (at ?c ?p))
    :effect (has ?c ?thing)
    :agent (?c))
	
  (:action pickup-gun
	:parameters (?c1 - char ?g - gun ?p - place)
	:precondition (and 
			(at ?g ?p) (at ?c1 ?p) (alive ?c1))
	:effect (and
		(has ?c1 ?g) (not (holstered ?g)))
	:agents (?c1)
  )
  
  (:action offer-drink
	:parameters (?c1 - bartender ?c2 - char ?p - place)
	:precondition (and (alive ?c1) (alive ?c2) (at ?c1 ?p) (at ?c2 ?p))
	:effect ()
	:agents (?c1))
  
  (:action help-up
	:parameters (?c1 - char ?c2 - char ?p - place)
	:precondition (and (alive ?c1) (alive ?c2) (at ?c1 ?p) (at ?c2 ?p) (not (standing ?c2)) (allies ?c1 ?c2))
	:effect (and (standing ?c2))
	:agents (?c1 ?c2))
	
  (:action cock-gun
	:parameters (?c1 - char ?g - gun)
	:precondition (and (has ?c1 ?g) (not (cocked ?g)) (alive ?c1) (not (holstered ?g)))
	:effect (cocked ?g)
	:agents (?c1))
	
  (:action wince
	:parameters (?c1 - char)
	:precondition (provoked ?c1)
	:effect ()
	:agents ())
)