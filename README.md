# 🐞 tinybug

**Mutation Testing Platform for Measuring Test Effectiveness**

---

## 🧠 What is tinybug?

**tinybug** is a platform for **mutation testing** — a technique to **measure how effective your tests really are** at catching bugs.

Modern development teams often focus on code coverage, but **code coverage ≠ bug detection**. Tests might run the code, but do they actually validate the behavior? Many tests pass even when the code they're covering is broken — due to poor assertions, missing checks, or lack of scenario diversity.

That’s where **tinybug** comes in.

## 💡 What is Mutation Testing?

Mutation testing works by **injecting small, artificial bugs (mutations)** into your codebase — particularly in code that’s already covered by your tests — and then running the tests again.

If the tests **fail**, great — they’re doing their job.  
If the tests **still pass**, that suggests **a gap in your test effectiveness**.

It helps answer:  
**"If this code had a bug, would our tests even catch it?"**

More on mutation testing:
- [Wikipedia: Mutation Testing](https://en.wikipedia.org/wiki/Mutation_testing)
- [Beginner’s Guide (Case Lab)](https://medium.com/@case_lab/mutation-testing-a-beginners-guide-41b731dc601e)
- [Google’s Mutation Testing at Scale (2017)](https://research.google/pubs/state-of-mutation-testing-at-google/)
- [PIT (for Java)](https://pitest.org/)
- [Stryker (for JS, TS, and more)](https://stryker-mutator.io/docs/)

## 🤖 Why Now?

Mutation testing has been around for decades, but hasn’t seen broad adoption due to:
1. **Low baseline coverage** in many teams.
2. **High cost** — mutation testing multiplies test execution time.
3. **Lack of approachable tooling** — existing tools like [Stryker](https://stryker-mutator.io) are powerful, but onboarding and usage at scale can be rough.

But the landscape is changing:
- **Code coverage is improving** across the industry.
- **Test automation is easier** than ever with modern CI/CD.
- **AI can now generate tests** — but how do we trust *those* tests?

If AI writes your tests, how do you know if *they're any good*?

Mutation testing is one of the best ways to evaluate **AI-generated tests** — by seeing whether they can detect meaningful failures in code.

## 🎯 Goal of tinybug

To provide a mutation testing platform that is:

- 🪶 **Lightweight** – minimal setup, easy integration  
- 🧪 **Test-focused** – measure what your tests *actually* validate  
- 🔍 **Insightful** – useful, actionable reports  
- 💻 **AI-relevant** – help assess the quality of AI-generated tests  

## 🔧 Status

This is an early-stage, work-in-progress project.

Stay tuned as we build out:
- Mutation operator framework
- Test orchestration and result tracking
- Mutation-aware reporting
- CI integration
- Dashboard & analytics

## 📄 License

MIT
