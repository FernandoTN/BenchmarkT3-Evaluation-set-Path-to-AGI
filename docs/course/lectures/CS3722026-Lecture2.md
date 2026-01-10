# CS3722026-Lecture2


## Page 1

CS372 AGI Winter 2026
Lecture 2: Causal Reasoning
Why Causality Requires More Than Data
Edward Y. Chang
Computer Science, Stanford University
January 7,2026
Stanford CS372 echang@cs.stanford.edu 1/46

## Page 2

Lecture Outline
1.Simpson’s Paradox— Why correlation̸= causation
2.Causal Models— DAGs, confounders, and what we need
3.Pearl’s Ladder— Three levels of causal reasoning
4.LLM Benchmarks— Impressive results, hidden problems
5.Failure Patterns— Four ways LLMs fail at causality
Stanford CS372 echang@cs.stanford.edu 2/46

## Page 3

Lecture Outline
1.Simpson’s Paradox— Why correlation̸= causation
2. Causal Models — DAGs, confounders, and what we need
3. Pearl’s Ladder — Three levels of causal reasoning
4. LLM Benchmarks — Impressive results, hidden problems
5. Failure Patterns — Four ways LLMs fail at causality
Stanford CS372 echang@cs.stanford.edu 3/46

## Page 4

The Paradox: Which Job-Training Program is Better?
Overall Employment Rates:
Program A Program B
Overall Employment Rate40% 50%
Obvious conclusion:Program B is more effective, better
But wait... Breaking down by experience level:
Program A Program B Total
Experienced 80% employed (n=200) 70% employed (n=600) 800
Entry-level 30% employed (n=800) 20% employed (n=400) 1200
Participants1000 1000 2000
Program A is better in EVERY subgroup, yet worse overall.
How is this possible?
Stanford CS372 echang@cs.stanford.edu 4/46

## Page 5

The Paradox: Which Job-Training Program is Better?
Overall Employment Rates:
Program A Program B
Overall Employment Rate40% 50%
Obvious conclusion:Program B is more effective, better
But wait... Breaking down by experience level:
Program A Program B Total
Experienced 80% employed (n=200) 70% employed (n=600) 800
Entry-level 30% employed (n=800) 20% employed (n=400) 1200
Participants1000 1000 2000
Program A is better in EVERY subgroup, yet worse overall.
How is this possible?
Stanford CS372 echang@cs.stanford.edu 4/46

## Page 6

The Hidden Numbers: Unequal Group Sizes
Program A Program B Total
Experienced 160/200 (80%) 420/600 (70%) 800
Entry-level 240/800 (30%) 80/400 (20%) 1200
Total Employed400/1000 (40%) 500/1000 (50%)
The asymmetry:
▶ Program A was given mostly toentry-levelparticipants (800 of 1000)
▶ Program B was given mostly toexperiencedparticipants (600 of 1000)
The aggregated data mixes apples and oranges
Experience level acts as aconfounding variable— it influences both program
assignment and outcome.
Stanford CS372 echang@cs.stanford.edu 5/46

## Page 7

The Causal Graph Explains Everything
Wrong mental model:
Program Employment
If this were true, B would be better
Correct causal structure:
Experience
Program Employment
Experience is a confounder:
▶ Experience→Program (assignment policy routes entry-level to A)
▶ Experience→Employment (entry-level harder to employ)
The causal question:If we assign Program A vs B to thesame mixof experience
levels, which yields higher employment?
→The subgroup analysis (controlling for experience)
Stanford CS372 echang@cs.stanford.edu 6/46

## Page 8

The Lesson for AGI
The “correct” answer depends on the causal question:
Question Correct Analysis
“Which programwas associated with
better outcomes?”
Aggregate (B looks better)
“Whichcausesbetter outcomes?” Stratified (A is better)
Why LLMs fail here:
▶ Both are correct for different questions, but only one is stable under intervention
▶ The data alone cannot tell you which to use
▶ Needcausal modelto decide whether to condition on Experience
Key insight: Causal reasoning requires structure beyond the data
Stanford CS372 echang@cs.stanford.edu 7/46

## Page 9

Lecture Outline
1. Simpson’s Paradox — Why correlation̸= causation
2.Causal Models— DAGs, confounders, and what we need
3. Pearl’s Ladder — Three levels of causal reasoning
4. LLM Benchmarks — Impressive results, hidden problems
5. Failure Patterns — Four ways LLMs fail at causality
Stanford CS372 echang@cs.stanford.edu 8/46

## Page 10

Key Causal Definitions
Confounder
Z
X Y
“Mixes things up”
Common cause of X and Y
Mediator
X Z Y
“Go-between”
On the causal pathway
Collider
Z
X Y
“Arrows collide into Z”
Common effect of X and Y
DAG(Directed Acyclic Graph): Arrows show cause→effect; no cycles allowed
Backdoor Path:Any path from X to Y that begins with an arrowintoX. If open,
induces non-causal association. Hot Weather
Ice Cream Drowning
spurious!
Backdoor path (Ice Cream←Hot Weather→Drowning)looks likecausation
Stanford CS372 echang@cs.stanford.edu 9/46

## Page 11

Mediator Example: How Programs Improve Employment
Question:How does a job training program lead to employment?
Program Skills Employment
direct?
Skills as Mediator:The program’s effect flowsthroughskill development.
Examples of mediating skills:
▶ Technical certifications
▶ Networking / social capital
▶ Interview preparation
▶ Resume building
Why mediators matter:
▶ Do NOT adjust for mediators when
estimating total effect
▶ Adjusting blocks the causal pathway!
▶ Mediators explainhowcauses work
Confounder: adjust to remove bias. Mediator: don’t adjust (blocks the effect).
Stanford CS372 echang@cs.stanford.edu 10/46

## Page 12

DAG Constraints: What’s Forbidden and How to Handle It
Forbidden: Cycles
X Y
X
YZ
Violates “Acyclic” in DAG
Real feedback loops exist (e.g., poverty↔
health)
Solution: Time-Unrolling
Xt Yt Xt+1 Yt+1
Feedback unrolled over time — now acyclic!
Other approaches:
▶ Equilibrium / steady-state models
▶ Dynamic Bayesian networks
▶ Structural equation models (SEM)
DAGs are limited but powerful. For cycles: add time or use specialized models.
Stanford CS372 echang@cs.stanford.edu 11/46

## Page 13

Complex DAGs: Mixing Confounders, Mediators, and Colliders
Example 1: Job Training
Age
Program
Skills
Employment
Interviewed
▶ Age:Confounder
▶ Skills:Mediator
▶ Interviewed:Collider
Example 2: Education & Earnings
Family Income
Education
Skills
Earnings
Elite Hire
▶ Family Income:Confounder
▶ Skills:Mediator
▶ Elite Hire:Collider
Stanford CS372 echang@cs.stanford.edu 12/46

## Page 14

What “Models” Do We Need?
These are layers, not alternatives:
Domain Knowledge
DAG(qualitative: X→Y)
Confounders List
Structural Equations (Y = f(X,ϵ))
Full Structural Causal Model (SCM)
informs
identifies
add functions
combines into
←Level 2(Intervention)
Sufficient forP(Y|do(X))
←Level 3(Counterfactual)
Required for “what if I had... ”
Stanford CS372 echang@cs.stanford.edu 13/46

## Page 15

Why We Focus on DAG
Domain Knowledge
DAG
... Structural Equations ... SCM
DAG is the foundational gap:
▶ LLMs are trained on observational prediction — no interventional semantics
▶ Without DAG, cannot distinguish confounder / mediator / collider
▶ All downstream steps depend on having the DAG first
What each level requires:
▶ Level 2(Intervention): DAG is sufficient — do-calculus works on the graph
▶ Level 3(Counterfactual): Need full SCM with structural equations
This course: How can LLMs help construct DAGs? Where do they fail?
Stanford CS372 echang@cs.stanford.edu 14/46

## Page 16

Can LLMs Help Construct Causal Graphs?
What LLMs can do:
▶ Suggest candidate variables from domain knowledge
▶ Propose edges based on known relationships in training data
▶ Generate hypotheses: “Age might confound the relationship”
What LLMs cannot do:
▶ Validate causal direction from data alone: requires assumptions or interventions
▶ Guarantee complete confounders: may propose plausible ones, but not exhaustive
▶ Distinguish correlation from causation: fundamentally observational training
A hybrid approach (roadmap preview):
1.LLM:Generate candidate variables and initial graph structure
2.Causal Discovery Algorithms:Test conditional independencies in data
3.Human Expert: Validate, add domain constraints, resolve conflicts
4.Do-Calculus:ComputeP(Y|do(X)) from final graph (covered next segment)
Stanford CS372 echang@cs.stanford.edu 15/46

## Page 17

Can LLMs Help Construct Causal Graphs?
What LLMs can do:
▶ Suggest candidate variables from domain knowledge
▶ Propose edges based on known relationships in training data
▶ Generate hypotheses: “Age might confound the relationship”
What LLMs cannot do:
▶ Validate causal direction from data alone: requires assumptions or interventions
▶ Guarantee complete confounders: may propose plausible ones, but not exhaustive
▶ Distinguish correlation from causation: fundamentally observational training
A hybrid approach (roadmap preview):
1.LLM:Generate candidate variables and initial graph structure
2.Causal Discovery Algorithms:Test conditional independencies in data
3.Human Expert: Validate, add domain constraints, resolve conflicts
4.Do-Calculus:ComputeP(Y|do(X)) from final graph (covered next segment)
Stanford CS372 echang@cs.stanford.edu 15/46

## Page 18

Can LLMs Help Construct Causal Graphs?
What LLMs can do:
▶ Suggest candidate variables from domain knowledge
▶ Propose edges based on known relationships in training data
▶ Generate hypotheses: “Age might confound the relationship”
What LLMs cannot do:
▶ Validate causal direction from data alone: requires assumptions or interventions
▶ Guarantee complete confounders: may propose plausible ones, but not exhaustive
▶ Distinguish correlation from causation: fundamentally observational training
A hybrid approach (roadmap preview):
1.LLM:Generate candidate variables and initial graph structure
2.Causal Discovery Algorithms:Test conditional independencies in data
3.Human Expert: Validate, add domain constraints, resolve conflicts
4.Do-Calculus:ComputeP(Y|do(X)) from final graph (covered next segment)
Stanford CS372 echang@cs.stanford.edu 15/46

## Page 19

Real-World Example: UC Berkeley Admissions (1973)
Aggregate data suggested gender discrimination:
Admission Rate
Male Applicants 44%
Female Applicants 35%
But department-level analysis revealed:
▶ Women hadequal or higheradmission rates in most departments
▶ Women disproportionately applied to highly competitive majors
▶ Men disproportionately applied to less competitive departments
The confounder:Department choice
“Department”, a confounder affects both acceptance probability and application distribution.
Same paradox, different domain — the pattern is universal
Stanford CS372 echang@cs.stanford.edu 16/46

## Page 20

Real-World Example: UC Berkeley Admissions (1973)
Aggregate data suggested gender discrimination:
Admission Rate
Male Applicants 44%
Female Applicants 35%
But department-level analysis revealed:
▶ Women hadequal or higheradmission rates in most departments
▶ Women disproportionately applied to highly competitive majors
▶ Men disproportionately applied to less competitive departments
The confounder:Department choice
“Department”, a confounder affects both acceptance probability and application distribution.
Same paradox, different domain — the pattern is universal
Stanford CS372 echang@cs.stanford.edu 16/46

## Page 21

Lecture Outline
1. Simpson’s Paradox — Why correlation̸= causation
2. Causal Models — DAGs, confounders, and what we need
3.Pearl’s Ladder— Three levels of causal reasoning
4. LLM Benchmarks — Impressive results, hidden problems
5. Failure Patterns — Four ways LLMs fail at causality
Stanford CS372 echang@cs.stanford.edu 17/46

## Page 22

Pearl’s Ladder of Causation
Three Levels:
Level 3: Counterfactual
P(yx |x′,y ′) — “What if I had...?”
Unsupported without SCM
Level 2: Intervention
P(Y|do(X)) — “What if I do...?”
Unsupported without causal graph + assumptions
Level 1: Association
P(Y|X) — “What if I see...?”
✓LLMs
Pearl & Mackenzie (2018):“The Book of Why”
Stanford CS372 echang@cs.stanford.edu 18/46

## Page 23

Why the Levels are Provably Distinct
Causal Hierarchy (Bareinboim et al., 2020):
Level-1 observational distributions cannot identify Level-2 interventional or Level-3
counterfactual quantities without additional assumptions or experimental information.
CS372 will cover techniques that make such assumptions explicit and testable.
What observation tells you:
▶ Among those whoended upin
Program A, some were employed
▶ P(Y=1|T=A) = 0.40
What observation cannot tell you:
▶ If weassignparticipants to Program
A, what isP(Y=1|do(T=A))?
▶ For a specific person who took A
and was employed, wouldYhave
been 1 underdo(T=None)?
Why?In observational data, groups differ due to selection/confounding (e.g.,
experience level), so in generalP(Y|T)̸=P(Y|do(T)).
Notation:Tis the program variable; we reserveP(·) for probability.
Stanford CS372 echang@cs.stanford.edu 19/46

## Page 24

Why the Levels are Provably Distinct
Causal Hierarchy (Bareinboim et al., 2020):
Level-1 observational distributions cannot identify Level-2 interventional or Level-3
counterfactual quantities without additional assumptions or experimental information.
CS372 will cover techniques that make such assumptions explicit and testable.
What observation tells you:
▶ Among those whoended upin
Program A, some were employed
▶ P(Y=1|T=A) = 0.40
What observation cannot tell you:
▶ If weassignparticipants to Program
A, what isP(Y=1|do(T=A))?
▶ For a specific person who took A
and was employed, wouldYhave
been 1 underdo(T=None)?
Why?In observational data, groups differ due to selection/confounding (e.g.,
experience level), so in generalP(Y|T)̸=P(Y|do(T)).
Notation:Tis the program variable; we reserveP(·) for probability.
Stanford CS372 echang@cs.stanford.edu 19/46

## Page 25

What Each Level Requires
LevelName Question Type Requires LLM?
1 AssociationP(Y|X) Observational data✓
2 InterventionP(Y|do(X)) Causal graph + adjustment limited
3 CounterfactualP(y x |x′,y ′) Full structural model×
Examples:
Level Example Question
1 “Do participants in Program A tend to get employed?”
2 “If we assign this person to Program A, what is their employment probability?”
3 “This person did Program A and got employed. Would they have without it?”
Key insight:LLMs trained on text learn Level-1 patterns. Levels 2-3 requirereasoning
about causal structure — not pattern retrieval.
Stanford CS372 echang@cs.stanford.edu 20/46

## Page 26

Two Different Questions
Simpson’s Paradox gives contradictory answers because it mixes two questions.
Question Quantity
Among those who enrolled in A, what frac-
tion were employed?
P(Y|T=A)
If we assign participants to A, what em-
ployment rate would result?
P(Y|do(T=A))
▶ After-the-fact (observational):describes what we observed in the data,
P(Y|T).
▶ Policy decision (interventional):predicts what would happen under an
assignment policy,P(Y|do(T)). This requires extra work: state assumptions,
identify and adjust for confounders, and produce a defensible analysis for
stakeholders or regulators.
Decision-making needsP(Y|do(T)), not justP(Y|T).
Stanford CS372 echang@cs.stanford.edu 21/46

## Page 27

WhyP(Y|T= A) Is Confounded
The causal structure:
Experience
T Y
assignment
What happened:
▶ Program A assigned mostly to
entry-level
▶ Program B assigned mostly to
experienced
P(Y|T=A)mixes together:
1. Effect of program on employment
2. Effect of experience on program assignment
3. Effect of experience on employment
The confounding path:
T←Experience→Y
This “backdoor path” creates spurious association!
Stanford CS372 echang@cs.stanford.edu 22/46

## Page 28

WhyP(Y|T= A) Is Confounded
The causal structure:
Experience
T Y
assignment
What happened:
▶ Program A assigned mostly to
entry-level
▶ Program B assigned mostly to
experienced
P(Y|T=A)mixes together:
1. Effect of program on employment
2. Effect of experience on program assignment
3. Effect of experience on employment
The confounding path:
T←Experience→Y
This “backdoor path” creates spurious association!
Stanford CS372 echang@cs.stanford.edu 22/46

## Page 29

The do-Operator: Graph Surgery
“do(T=A)”= Assign everyone to Program A,regardless of experience
Before: Observational
Experience
T Y
Experience determines program
P(Y|T) is confounded
⇒
surgery
After:do(T=A)
Experience
T Y
cut!
Tisset by intervention(not by
Experience)
Backdoor from Experience is cut
Key insight:Cutting the incoming arrow removes confounding from Experience
because assignment is no longer determined by Experience.
Stanford CS372 echang@cs.stanford.edu 23/46

## Page 30

Cut the Backdoor Path (Design)
Backdoor in our running example:T←E→Y(Eaffects bothTandY)
Cut by design: change howTis assigned
▶ Goal:makeTindependent ofEby construction
▶ Methods:
▶ Randomized assignment
▶ Stratified randomization (randomize within eachElevel)
▶ Rerandomization until balance criteria are met
▶ Interpretation:closest practical version ofdo(T=·)
Note: even with randomization, you may see 55/45 splits due to chance. That is not
confounding; it is finite-sample imbalance.
One-liner:Confounding is prevented byhow we assign T.
Cutis a property of the assignment mechanism.
Stanford CS372 echang@cs.stanford.edu 24/46

## Page 31

Block the Backdoor Path (Analysis)
Backdoor in our running example:T←E→Y
Block by analysis: keep data, remove the spurious path
▶ Goal:compare like strata to block spuriousT–Yassociation
▶ Methods:
▶ Stratify onEand reweight to targetP(E)
▶ Matching onE(and other confounders)
▶ Inverse propensity weighting
▶ Regression adjustment with pre-treatment covariates
▶ Limitation:works only for measured confounders (unknownUcan still bias)
One-liner:Confounding is handled byhow we adjustin the analysis.
Blockis a property of the estimation strategy given a graph.
Stanford CS372 echang@cs.stanford.edu 25/46

## Page 32

The Backdoor Adjustment Formula
Problem:We can’t actually assign everyone to Program A.
Solution:Use observed data + graph structure tocompute P(Y|do(T)).
Backdoor Adjustment Formula
P(Y|do(T=A)) =
∑
e
P(Y|T=A,E=e)·P(E=e)
Term Meaning Source
P(Y|T=A,E=e) Effect within each stratum Stratified data
P(E=e) Target population distribution Overall data∑
e Weighted average Marginalization
Intuition:Within each experience level, there’s no confounding. So we compute the
effect per stratum, then average over the population.
Assumes: no unmeasured confounding, positivity (each stratum has both programs).
Stanford CS372 echang@cs.stanford.edu 26/46

## Page 33

Step-by-Step Calculation
Step 1: Stratified effectsP(Employed|T,Experience)
Program A Program B
Experienced 160/200 =0.80420/600 =0.70
Entry-level 240/800 =0.3080/400 =0.20
Step 2: Target population distributionP(Experience)
Experienced 800/2000 =0.40
Entry-level 1200/2000 =0.60
Step 3: Apply formula
P(Y|do(T=A)) = 0.80×0.40 + 0.30×0.60 = 0.32 + 0.18 =0.50
P(Y|do(T=B)) = 0.70×0.40 + 0.20×0.60 = 0.28 + 0.12 =0.40
Stanford CS372 echang@cs.stanford.edu 27/46

## Page 34

The Verdict: Paradox Resolved
Program A Program B
ObservationalP(Y|T) 40% 50%←looks better
CausalP(Y|do(T)) 50%←actually better 40%
Observational (confounded):
▶ B looks better (50% ¿ 40%)
▶ But B participants were mostly
experienced!
Causal (adjusted):
▶ A is truly better (50% ¿ 40%)
▶ After accounting for experience
For this target population:P(Y|do(T=A))>P(Y|do(T=B))
Stanford CS372 echang@cs.stanford.edu 28/46

## Page 35

Why “Target Population” Matters
The formula usesP(E=e) — butwhich population’s distribution?
Same program effect per stratum, different target populations:
% Exp’d % EntryP(Y|do(T=A))
Region 1 (tech hub) 90% 10% 0.80×0.9 + 0.30×0.1 =0.75
Region 2 (rural) 10% 90% 0.80×0.1 + 0.30×0.9 =0.35
Overall population 40% 60% 0.80×0.4 + 0.30×0.6 =0.50
Key insight:
▶ Same program, same per-stratum effect
▶ Different overall rates due to different experience mix
▶ You must specify: “Effect for whom?”
Stanford CS372 echang@cs.stanford.edu 29/46

## Page 36

Why Causal Graphs Are Essential (1): What to Adjust For
The Backdoor Criterion(Pearl): Adjust for variables that block all backdoor paths.
Our example:
Experience
T Y
Backdoor path: T←E→Y
Adjust for E✓
More complex:
U
E
T Y
Backdoor: T←E→Y
Adjust for E (blocks path)
U not needed here —but what if U affects
Y directly?
Without the graph, how would you know WHAT to adjust for?
Stanford CS372 echang@cs.stanford.edu 30/46

## Page 37

Why Causal Graphs Are Essential (2): Confounders vs Colliders
Adjusting for the wrong variable creates bias!
Confounder (adjust = good)
Experience
T Y
Adjustingremovesbias
(Blocks backdoor path)
Collider (adjust = bad)
Interviewed
T Ability
Adjustingcreatesbias
(Opens a path that was closed!)
Collider bias example:
▶ Both program participation AND high ability→get interviewed
▶ Among interviewed: spurious negative T–Ability correlation appears
▶ This is “Berkson’s paradox” / selection bias
Data alone cannot tell you which is which — only the causal graph can
Stanford CS372 echang@cs.stanford.edu 31/46

## Page 38

Summary: The do-Calculus Recipe
1.Draw the causal graph
From domain knowledge — what causes what?
2.Identify backdoor paths
Paths from T to Y that start with an arrowintoT
3.Find adjustment set
Variables that block ALL backdoor paths (use backdoor criterion)
4.Apply the formulaP(Y|do(T)) =
∑
z P(Y|T,Z=z)·P(Z=z)
5.Interpret
This is thecausal effect— what happens if we intervene
No causal graph⇒Don’t know what to adjust for⇒Cannot resolve Simpson’s
With causal graph⇒Backdoor criterion⇒Principled causal inference
Stanford CS372 echang@cs.stanford.edu 32/46

## Page 39

Counterfactuals: The Three-Step Process (Level 3)
Question:“Person did Program A and got employed. Would they have been
employedwithoutthe program?”
This requires reasoning about aspecific individualin ahypothetical world.
Step 1: Abduction
InferUfrom evidence
Step 2: Action
Applydo(T= None)
Step 3: Prediction
ComputeYin new world
Example:
1.Abduction:Person did Program A, got employed⇒infer their latent factorsU
2.Action:Imaginedo(T= None) — surgery on the graph
3.Prediction:With their specificU, would they have been employed? Compute
Ydo(T=None)
Requires full Structural Causal Model (SCM) with functional equations, not just DAG
Stanford CS372 echang@cs.stanford.edu 33/46

## Page 40

Discussion: Can We Ever Be Certain?
Scenario:Observational study showsP(Employed|Program A) = 0.40
Question 1:Can you tell a participant: “You have 40% chance of employment if you
enroll in Program A”?
A. Yes — the data clearly shows 40%
B. No — this assumes no confounding
C. It depends on the study design
Question 2:If correlation is100%(everyone in Program A got employed), can we
now be certain the program works?
A. Yes — 100% is definitive proof
B. No — could still be perfect confounding
C. Only if we have a large sample size
Stanford CS372 echang@cs.stanford.edu 34/46

## Page 41

Discussion: Can We Ever Be Certain?
Scenario:Observational study showsP(Employed|Program A) = 0.40
Question 1:Can you tell a participant: “You have 40% chance of employment if you
enroll in Program A”?
A. Yes — the data clearly shows 40%
B. No — this assumes no confounding
C. It depends on the study design
Question 2:If correlation is100%(everyone in Program A got employed), can we
now be certain the program works?
A. Yes — 100% is definitive proof
B. No — could still be perfect confounding
C. Only if we have a large sample size
Stanford CS372 echang@cs.stanford.edu 34/46

## Page 42

Discussion: Can We Ever Be Certain?
Question 3:We adjusted for Experience. What if there’s anunknown confounder U
(e.g., neighborhood GDP, motivation)?
A. No problem — adjusting for Experience is enough
B. Our causal estimate could be completely wrong
C. We can never do causal inference without RCTs
Question 4:How can we EVER be confident about causation?
A. Randomized Controlled Trials (RCTs) — break ALL confounding by design
B. Explicit causal assumptions + sensitivity analysis
C. Multiple converging lines of evidence
D.All of the above
Stanford CS372 echang@cs.stanford.edu 35/46

## Page 43

Discussion: Can We Ever Be Certain?
Question 3:We adjusted for Experience. What if there’s anunknown confounder U
(e.g., neighborhood GDP, motivation)?
A. No problem — adjusting for Experience is enough
B. Our causal estimate could be completely wrong
C. We can never do causal inference without RCTs
Question 4:How can we EVER be confident about causation?
A. Randomized Controlled Trials (RCTs) — break ALL confounding by design
B. Explicit causal assumptions + sensitivity analysis
C. Multiple converging lines of evidence
D.All of the above
Stanford CS372 echang@cs.stanford.edu 35/46

## Page 44

Discussion: Key Takeaways
The uncomfortable truth about unknown confounders:
▶ We cannever be certainwe’ve identified all confounders
▶ Domain expertise helps, but isn’t foolproof
▶ This is why we muststate assumptions explicitly
What we can do:
▶ RCTs— break ALL confounding (known and unknown) by design
▶ Sensitivity analysis— “How wrong could we be if U exists?”
▶ Multiple evidence— different studies, different potential confounders
▶ Negative controls— test assumptions where we know the answer
Causal inference requires humility: state your assumptions, quantify uncertainty
Stanford CS372 echang@cs.stanford.edu 36/46

## Page 45

Lecture Outline
1. Simpson’s Paradox — Why correlation̸= causation
2. Causal Models — DAGs, confounders, and what we need
3. Pearl’s Ladder — Three levels of causal reasoning
4.LLM Benchmarks— Impressive results, hidden problems
5. Failure Patterns — Four ways LLMs fail at causality
Stanford CS372 echang@cs.stanford.edu 37/46

## Page 46

The Good News: LLMs Score High on Several Causal Benchmarks
Kıcıman et al. (TMLR, 2023):strong accuracy on multiple tasks/benchmarks.
Task Benchmark / Setup GPT-4
Pairwise causal discovery T ¨ubingen Cause-Effect Pairs
(bivariate direction)
97%
Counterfactual reasoning CRASS counterfactual query benchmark
(physics/logic/common sense)
92%
Event causality 15 standard vignettes
(necessary vs sufficient cause)
86%
▶ They also report robustness checks and generalization to newer datasets created
after training cutoff.
▶ LLMs can help draft graphs and causal context from natural language.
So... problem solved?
Stanford CS372 echang@cs.stanford.edu 38/46

## Page 47

The Bad News: High Scores Can Hide Fragility
Same study, same models:high average accuracy does not imply reliable causal
reasoning.
What they observe:
▶ Unpredictable failure modeseven on tasks where accuracy is high
▶ Over-reliance on text cues:the paper notes behavior driven bytext metadata
▶ Data neglect:they explicitly warn that LLMs canignore the actual data
Implication:
▶ High benchmark scores + occasional sharp failures is consistent with strong
pattern completion, not a dependable causal procedure.
Stanford CS372 echang@cs.stanford.edu 39/46

## Page 48

CS372 Project: Scaling Causal Benchmarks for AGI Research
Goal:Scale the T3 Causal Benchmark from 454→5,000+ vignettes for rigorous
algorithm evaluation.
Assignment 1
Scale to V1
Assignment 2
Peer Review
Assignment 3
Quality Control
Final Phase
Algorithm Testing
Why this matters:
▶ Current benchmarks (454 cases) lack statistical power for NeurIPS-level claims
▶ Testing RCA, UCCT, and novel algorithms requires diverse, high-quality vignettes
▶ You will contribute to publishable research infrastructure
T3 Benchmark:10 categories×3 levels (L1 Association, L2 Intervention, L3
Counterfactual)
Stanford CS372 echang@cs.stanford.edu 40/46

## Page 49

Assignment 1: Scale T3 Benchmark (V1)
Timeline:1 weekDeliverable:V1 of expanded vignettes + quality analysis
Team Structure:
▶ Teams of 6 student, each team assigned1 of 10 categories
▶ Target:∼10×increase per category
Your Tasks:
1.Analyzeexisting vignettes in your assigned category (difficulty, coverage)
2.Generatenew vignettes for L1, L2, and L3 levels
3.Documentquality concerns, ambiguities, or gaps discovered
4.DeliverV1 dataset + quality analysis report
What happens next:
▶ A2:Teams swap categories for cross-review, editing, and justification
▶ A3:Quality control phase — reassigned by expertise (your major matters!)
▶ Final:LLM validation runs + test your own reasoning algorithms
Stanford CS372 echang@cs.stanford.edu 41/46

## Page 50

Failure Pattern 1: Sensitivity to Wording
The problem:Small wording changes can change outcomes.
Evidence (Kıcıman et al., 2023):
▶ Redaction probing shows key causal trigger words (e.g., “changing”, “causes”)
strongly affect accuracy.
▶ Even redacting seemingly minor words can hurt accuracy, suggesting sensitivity to
phrasing and grammar.
Why this matters:A causal reasoner should be invariant to paraphrase when meaning
is preserved. Here, behavior indicates reliance on surface cues and instruction patterns.
Mapping to Pearl:this looks like Level-1 style sensitivity, not stable Level-2 reasoning.
Stanford CS372 echang@cs.stanford.edu 42/46

## Page 51

Failure Pattern 2: Semantic Cues Override Data
The problem:When labels or context carry strong connotations, models may follow
semantics rather than the evidence.
Evidence:
▶ LLMs can pick an answer aligned with label meaning even when the data strongly
supports the opposite conclusion.
Why this matters:If the model is not reliably using the dataset and assumptions to
reason about confounding, it is not robustly answering an interventional question.
Mapping to Pearl:Level-2 requires reasoning aboutP(Y|do(T)), not shortcuts
from text semantics.
Stanford CS372 echang@cs.stanford.edu 43/46

## Page 52

Failure Pattern 3: No Grounded Intervention Mechanism
The problem:Correct answers on famous confounding examples do not imply a
reliable ability to compute interventions.
What we observe in the literature:
▶ Models can look strong on benchmarks yet still show failures where they rely on
non-causal textual signals and can even ignore the underlying data representation.
Core gap:Without an explicit causal model (or a tool that enforces one), the system
has no guaranteed way to separateP(Y|X) fromP(Y|do(X)).
Pearl:distinguishing association from intervention is exactly the Level-1 vs Level-2
boundary.
Stanford CS372 echang@cs.stanford.edu 44/46

## Page 53

Failure Pattern 4: Simple, Unpredictable Mistakes
The problem:Even when average accuracy is high, LLMs can make simple mistakes
on specific inputs.
Example (from Kıcıman et al., 2023): necessity vs sufficiency slip
▶ On necessary/sufficient-cause vignettes, GPT-4 is often correct,
▶ but on some cases (e.g., the “short circuit” vignette), it applies the wrong
principle and fails.
Why this matters:
▶ The mistake is not a missing fact.
▶ It is an inconsistency in applying the causal criterion (which principle is relevant?).
Pearl’s Ladder link:
▶ Many vignette tasks are Level 2 to Level 3 flavored,
▶ Brittleness signals missing or unstable causal control, not just missing knowledge.
Stanford CS372 echang@cs.stanford.edu 45/46

## Page 54

Summary: High Scores, Fragile Causal Control
From Kıcıman et al., 2023:
LLMs exhibit unpredictable failure modes, and accuracy depends substantially
on the prompt used.
Failure Pattern Where it shows up Diagnosis
Brittleness to prompts Across tasks Sensitivity to surface form
Misread the data context Obs vs causal settings Prior patterns can override the dataset
No explicit intervention engine Level 2 questions No guaranteeddo(·) computation
Unpredictable logical slips Level 2/3 vignettes Unstable application of causal criteria
Takeaway:High benchmark scores do not imply reliable causal reasoning. They can
reflect partial, pattern-based competence with brittle control.
Stanford CS372 echang@cs.stanford.edu 46/46