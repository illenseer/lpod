% OPT: pareto
% AS: d f q

a ;; b ;; c :- p.
d ;; e.
f ;; g.
:- a.
p :- not q.
q :- not p.
