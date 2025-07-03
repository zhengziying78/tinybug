
### Q: where my code should be
A: 
1, it has to be git. I don't think one day we will support other version controls, like Mercury, Perforce, etc. Only git. 
2, it could be any git: public repo in github, private repo in github, repos in GitHub Enterprise, in other hosting services like gitlab, etc. As long as tinybug can access it. 

"As long as tinybug can access it" means two things: network connectivity, and the authn/authz. tinybug will be running in AWS. So the git repo has to be publicly aceessible, from networking perspective. Regarding authn/authz, I expect it to be some token/key that the repo owner provided for tinybug. 

The access is a part of the onboarding. The repo owner needs to provide the location of the repo, as well as the access (e.g. token/key).

Wrt the exact permissions, it depends. We will discuss more in details later. At a high level, 
- Tinybug needs to read, e.g. fetch, clone
- Tinybug might need to push to a remote branch. Not main or master. A development branch would be enough. That's for running the tests. Tinybug will make code change (aka mutation), push to a remote dev branch, then 


### Q: any specific git branching strategy?
A: Branching strategy like "git flow", "github flow", "trunk based deveopment", etc. don't make too much difference to tinybug. All tinybug needs to do is to able to run tests on a temporary code change. 
So it mainly depends on how the tests are triggered. 


### Q: any requirement to the test triggering?
A: there are many different ways a project triggers its tests. For example, 
- Run tests in GitHub. For example, create a pull request, and the tests run as a check, which is in a "workflow" in github. The workflow triggers on any pull request creation/update/merge, then the workflow will run the tests. This is where we need some more detailed thoughts/design: what's the interface between the test run and tinybug? How would tinybug get the test results (including details, like which test cases failed). 
- Run tests in other CI platforms, like Buildkite. The code is somewhere in a remote dev branch, and a build in BuildKite gets triggered. 

Maybe we can start with something simpler. 

One thing for sure: we want to run the tests in customer's test infra (e.g. github account, buildkite account, AWS machines, etc.). In a "bring your own resources" way. That will help us avoid lots of cost problems: it reduces tinybug's own cost, and it reduces the complexity of how do we charge users. Tinybug's resource (compute, storage, etc) is only for driving the mutation testing process, store the results (like which mutant is caught, which is uncaught, etc), etc. 


### Q: it only supports unit tests?
A: to certain degree, whether the tests is unit tests doesn't matter that much. Many test harnesses, like pytest, go test, junit, etc. can execute unit tests as well as integration tests. The tests itself is like a blackbox to tinybug:
- Input: given a git branch, start a github workflow, or a buildkite build
- Output: the test result, like X total test cases, Y passed, Z failed, and the list of Z failed test cases. 

We would highly recommend do this with unit tests. For a few reasons:
1. Cost. Measuring test effectiveness requires running the tests multiple times. For example, if we have 500 mutants, we will run the tests 500 times (of course, there will be some optimizations we can do). Integration tests are usually a lot more costly than unit tests. Another cost factor is time. Usually it takes less time to run unit tests than integration tests. Given we need to run the tests hundreds of times, time matters. 
2. Code coverage. Getting code coverage data of unit tests is much more straightforward, because the code (which includes the coverage instrumentation) is only on the local machine. Code coverage is useful because we want to make mutations on the lines that are covered by the tests. Tinybug wants to focus on test effectiveness, not code coverage. Tinybug doesn't want to put mutations on the uncovered lines. 
3. Stability. Unit tests usually is less flaky than integration tests. Although tinybug does have design to handle the noise due to test flakyness, less flakyness noise will still be better. 

So, _practically_, we only support unit tests. We will tell user, when onboarding, only specify the details for running unit tests (meaning: the code-under-test runs in the same process as the test case code). We will advise users to not use tinybug for integration tests. 

TODO: need to understand other tech stacks and how tests work there. For example, the js/ts web code and playright. 

### Q: do we also need code coverage data?
A: yes we need coverage data. Because we only want to put mutants on the covered lines. 
Tinybug could still work without coverage data. In that case, the test effectiveness result measureed by tinybug is no longer _just_ test effectiveness. It would be two factors combined: test effectiveness (i.e. in the room you do have a smoke detector, will the smoke detector alarm when there is fire in the room) and test coverage (i.e. do all the rooms have smoke detectors? Is there any room without smoke detector?)

Wrt where the coverage data come from, it depends on the language, and the test setup. 
A typical process can be, for a given repo,
- tinybug runs test effectiveness measurement on regular basis, like once a week (we really don't need that on per-commit basis). 
- In the beginning of a measurement run, tinybug will first run the tests with coverage. Tinybug will collect the coverage data. 
- Then, tinybug will create mutants based on that coverage data. 

### Q: what languages you support
A: we probably will begin with commonly used languages. Maybe CSharp, Java, Python and Golang to begin with. 
Then we can add other backend languages like Rust, C/C++. We later can also add frontend languages, like Javascript and Typescript. I guess for the first a few months, these languages will be good enough. 

### Q: mutator
A: we would use the mutators that are already available out there. We could also write our own mutators for each languages. The mutators will follow the same known patterns to create mutations. there are about 20+ different patterns (TODO: find these patterns. There is a paper for it)
In the future, we can also create mutants based on past bugs, etc. We can create bugs with AI (hmm.. that might be tricky, because we build tinybug because we don't know if we can trust the tests generated by AI. Now, we are using the mutants generated by AI, do we know if we can trust these mutants? --- TBD). 
In the beginning, we will stick to the "traditional" mutants.
There will be other kind of more 'advanced" mutants we can do. For example, bugs related to racing condition, multithread, etc. That's probably for the future when tinybug has already gain some successes.  


### Q: result
A: I haven't thought much about it. Maybe we can do something straightfoward, like:
- User opens a page of a run. The page shows that the run has used 500 mutants, and 150 of them are "caught" (i.e. some tests failed), and 350 of them are uncaught (meaning: no tests failed).
- User can see the list of these mutants (they can filter by caught/uncaught). Clicking each mutant, user can see the code. If we create 1 pull request for each mutant, then click a mutant on the list and user will see the pull request. 
- The result, of course, can be accessed by API, and/or via downloading a result file (e.g. in json or xml)


### Q: noise due to test flaky
A: tinybug can handle a little bit of test flaky. 
Tinybug will run the tests a few times, without any mutant, to understand which tests are flaky. 
One thing tinybug could do is: ignore the known-flaky tests. Of course, that will affect the accuracy of test effectiveness measurement. But that also sort of makes sense: in the real world, a flaky test is a less useful signal. When there is a bug, and a flaky test failed due to that bug, human would probably ignore that, thinking "that test case has not been very stable, and that failure is probably just a flake". At the end of the day, tinybug wants to measure whether the tests can catch the bug when there is one. 
Another thing tinybug could do is: automatically rerun the failed tests. 
Anyway, in the beginning (the proof-of-concept phase, as well as the MVP phase), we don't have to spend time on the test flaky thing. 