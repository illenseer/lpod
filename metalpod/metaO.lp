%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Copyright (C) 2015  Nils Pascal Illenseer                               %
%                                                                         %
% This program is free software: you can redistribute it and/or modify    %
% it under the terms of the GNU General Public License as published by    %
% the Free Software Foundation, either version 3 of the License, or       %
% (at your option) any later version.                                     %
%                                                                         %
% This program is distributed in the hope that it will be useful,         %
% but WITHOUT ANY WARRANTY; without even the implied warranty of          %
% MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           %
% GNU General Public License for more details.                            %
%                                                                         %
% You should have received a copy of the GNU General Public License       %
% along with this program.  If not, see <http://www.gnu.org/licenses/>.   %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% all combination strategies
cxopt(pareto).
cxopt(incl).
cxopt(card).

% all degrees
deg(D) :- show(_,satisfied(_,D)).
% all rules
rule(R) :- show(_,satisfied(R,_)).

% set strategy
strategy(O) :- show(_,optimize(O)), not optimize(_).
strategy(O) :- optimize(O).
% default strategy pareto
strategy(pareto) :- not strategy(O) : cxopt(O).

% verify dominance
bot :- equal(_).
bot :- worse(_).

% require non-existence of dominating answer set
:- not bot.


% Degrees for all rules
degCand(R,D) :- strategy(pareto),
                normal(A,B),
                hold(A),
                show(A,satisfied(R,D)).

degCounter(R,D) :- strategy(pareto),
                   normal(A,B),
                   true(lits(B)),
                   true(atom(A)),
                   show(A,satisfied(R,D)).


% Inverse degrees for all rules
invDegCand(R,D) :- strategy(incl;card),
                   normal(A,B),
                   not hold(A),
                   not body(B),
                   show(A,satisfied(R,D)).

invDegCounter(R,D) :- strategy(incl;card),
                      normal(A,B),
                      fail(atom(A)),
                      fail(lits(B)),
                      show(A,satisfied(R,D)).


%%%%%%%%%% Pareto-preferred

worse(pareto) :- strategy(pareto), degCand(R,D1), degCounter(R,D2), D1 < D2.

equal(pareto,R) :- strategy(pareto), degCand(R,D), degCounter(R,D).
equal(pareto) :- strategy(pareto), equal(pareto,R) : rule(R).


%%%%%%%%%% Inclusion-preferred

% rule with degree
rd(R,D) :- strategy(incl), show(_,satisfied(R,D)).

ndiff(R,D) :- strategy(incl), rd(R,D), invDegCounter(R,D).
ndiff(R,D) :- strategy(incl), rd(R,D), not invDegCand(R,D).

equal(incl,D) :- strategy(incl), deg(D), ndiff(R,D) : rd(R,D).
equal(incl) :- strategy(incl), equal(incl,D) : deg(D).

worse(incl,D) :- strategy(incl), rd(R,D),
                 invDegCounter(R,D), not invDegCand(R,D).
worse(incl) :- strategy(incl), worse(incl,D1),
               equal(incl,D2) : deg(D2), D2 < D1.

%%%%%%%%%% Cardinality-preferred

count(D,0) :- strategy(card),
              deg(D),
              #sum { -1,R1 : invDegCand(R1,D), rule(R1) ;
                      1,R2 : invDegCounter(R2,D), rule(R2) } >= 0.

count(D,1) :- strategy(card),
              deg(D),
              #sum { -1,R1 : invDegCand(R1,D), rule(R1) ;
                      1,R2 : invDegCounter(R2,D), rule(R2) } >= 1.

worse(card) :- strategy(card),
               count(D1,1),
               count(D2,0) : D1 > D2, deg(D2).

equal(card) :- strategy(card), count(D,0) : deg(D).


% hide od_atoms(_,_), od_body(_), satisfied(_,_) and optimize(_)
hide(A,od_atoms(R,D)) :- show(A,od_atoms(R,D)).
hide(A,od_body(R)) :- show(A,od_body(R)).
hide(A,satisfied(R,D)) :- show(A,satisfied(R,D)).
hide(A,optimize(O)) :- show(A,optimize(O)).
