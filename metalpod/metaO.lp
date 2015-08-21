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
deg(D) :- show(_,od_atoms(_,D)).
% all rules
rule(R) :- show(_,od_atoms(R,_)).

% set strategy
strategy(O) :- show(_,optimize(O)), not optimize(_).
strategy(O) :- optimize(O).
% default strategy pareto
strategy(pareto) :- not strategy(O) : cxopt(O).

% set generator
generator(G) :- show(_,generator(G)).

% verify dominance
bot :- equal(_).
bot :- worse(_).

% % require non-existence of dominating answer set
:- not bot.


% Degrees for all rules for generator split
degC(R,1) :- strategy(pareto),
             generator(split),
             choice(I,B),
             atoms(I,A),
             not body(B),
             show(A,od_atoms(R,1)).

degC(R,D) :- strategy(pareto),
             generator(split),
             choice(I,B),
             atoms(I,A),
             hold(A),
             show(A,od_atoms(R,D)).

degO(R,1) :- strategy(pareto),
             generator(split),
             choice(I,B),
             atoms(I,A),
             fail(lits(B)),
             show(A,od_atoms(R,1)).

degO(R,D) :- strategy(pareto),
             generator(split),
             choice(I,B),
             atoms(I,A),
             true(lits(B)),
             true(atom(A)),
             show(A,od_atoms(R,D)).

% Degrees for all rules for generator cabalar
degC(R,D) :- strategy(pareto),
             generator(cabalar),
             normal(A,B),
             hold(A),
             show(A,od_atoms(R,D)).

degO(R,D) :- strategy(pareto),
             generator(cabalar),
             normal(A,B),
             true(lits(B)),
             true(atom(A)),
             show(A,od_atoms(R,D)).

% Inverse degrees for all rules for generator split
invDegC(R,D) :- strategy(incl;card),
                generator(split),
                atoms(I,A),
                choice(I,B),
                not body(B),
                show(A,od_atoms(R,D)),
                deg(D), D>1.

invDegC(R,D) :- strategy(incl;card),
                generator(split),
                atoms(I,A),
                choice(I,B),
                body(B),
                show(A,od_atoms(R,D)),
                not hold(A).

invDegO(R,D) :- strategy(incl;card),
                generator(split),
                atoms(I,A),
                choice(I,B),
                fail(lits(B)),
                show(A,od_atoms(R,D)),
                D>1.

invDegO(R,D) :- strategy(incl;card),
                generator(split),
                atoms(I,A),
                choice(I,B),
                true(lits(B)),
                show(A,od_atoms(R,D)),
                fail(atom(A)).

% Inverse degrees for all rules for generator cabalar
invDegC(R,D) :- strategy(incl;card),
                generator(cabalar),
                normal(A,B),
                not hold(A),
                not body(B),
                show(A,od_atoms(R,D)).

invDegO(R,D) :- strategy(incl;card),
                generator(cabalar),
                normal(A,B),
                fail(atom(A)),
                fail(lits(B)),
                show(A,od_atoms(R,D)).


%%%%%%%%%% Pareto-preferred

worse(pareto) :- strategy(pareto), degC(R,D1), degO(R,D2), D1 < D2.

equal(pareto,R) :- strategy(pareto), degC(R,D), degO(R,D).
equal(pareto) :- strategy(pareto), equal(pareto,R) : rule(R).


%%%%%%%%%% Inclusion-preferred

% strategy for every degree
strategy(incl,D) :- strategy(incl), deg(D).

% verify dominance
chain(D1,D2) :- strategy(incl,D1), strategy(incl,D2), D1 < D2,
                #false : strategy(incl,D3), D1 < D3, D3 < D2.

check(D2) :- strategy(incl,D2), #false : chain(D1,D2).
check(D2) :- chain(D1,D2), check(D1), equal(incl,D1).

worse(incl) :- check(D1), worse(incl,D1).
equal(incl) :- check(D1), equal(incl,D1), #false : chain(D1,D2).

% rule with degree
rd(R,D) :- strategy(incl), show(_,od_atoms(R,D)).

ndiff(R,D) :- strategy(incl), rd(R,D), invDegO(R,D).
ndiff(R,D) :- strategy(incl), rd(R,D), not invDegC(R,D).

equal(incl,D) :- strategy(incl), deg(D), ndiff(R,D) : rd(R,D).
worse(incl,D) :- strategy(incl), rd(R,D), invDegO(R,D), not invDegC(R,D).


%%%%%%%%%% Cardinality-preferred

count(D,0) :- strategy(card),
              deg(D),
              #sum { -1,R1 : invDegC(R1,D), rule(R1) ;
                      1,R2 : invDegO(R2,D), rule(R2) } >= 0.

count(D,1) :- strategy(card),
              deg(D),
              #sum { -1,R1 : invDegC(R1,D), rule(R1) ;
                      1,R2 : invDegO(R2,D), rule(R2) } >= 1.

worse(card) :- strategy(card),
               count(D1,1),
               count(D2,0) : D1 > D2, deg(D2).

equal(card) :- strategy(card), count(D,0) : deg(D).


% hide od_atoms(_,_), od_body(_), generator(_) and optimize(_)
hide(A,od_atoms(R,D)) :- show(A,od_atoms(R,D)).
hide(A,od_body(R)) :- show(A,od_body(R)).
hide(A,optimize(O)) :- show(A,optimize(O)).
hide(A,generator(G)) :- show(A,generator(G)).
