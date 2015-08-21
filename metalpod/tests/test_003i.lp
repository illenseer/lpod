% OPT: incl
% AS: a d f p
% AS: d f q

a ;; b ;; c :- p.
d ;; e.
f ;; g.
p :- not q.
q :- not p.
