Before we continue working on PoC, I want to have a bit more clarity regarding the web. 

We need two webs:
1. A logged-out website. The landing page. The marketing material. The docs. etc. These are purely public static content. 
2. A logged-in site. That's for the real work. Like tinybug.ai/robinhood, tinybug.ai/coinbase, tinybug.ai/stripe, ... That's where they configure repos and tests, view measurement results, etc. 

Give me some technical solution suggestions. For example, 

- What's the tech stack to use? There are ton of web framework. I am leaning toward using Python, but also OK with any Javascript/Typescript things. I think the logged-out website doesn't matter too much, as there isn't much "logic". The logged-in site has more logic, more user interaction. Behind the logged-in site, there will be a backend. The backend has some database, interact with Temporal, etc. 

- For the logged-in site, if we use Python, I don't want to use Django. 

- I also want to know about the database access layer, which is a part of the backend. I want to spend less amount of time dealing with schema and schema migration (e.g. add columns, etc.). I do want to use some framework, and write less boilerplate code. But I don't want the database access layer to be too much a blackbox --- like Django. Django does too much funky things, and that's hard to debugging. 

Give me some thoughts on web. 

-----

Forgot one thing: hosting. 

I already have my domain name (tinybug.ai), registered in CloudFlare.

When it comes to hosting, lower cost is important. 

Then, I want reasonable amount of monitoring. I am not too worried about scalability, since it won't be very high traffic. It's a SaaS tools site. 

I am reasonably familiar with AWS and CI platforms. I do hope the updating process can be similar. But if it requires a little bit of work to rollout web changes (including logged-out site and logged-in site), I am OK with it. 



Btw, I don't care if the static site and the logged-in site are hosted together. If they don't have to, they don't have to. As long as it's: low cost, reasonable monitoring/observability, and not too much work to rollout.

With these, recommend hosting solution for me. 


------

With such web (including logged-in site and the backend) and hosting solution, how do my staging/canary look like? I don't want it to be unneccessarily too fancy: tinybug.ai hasn't reached Product-market fit (PMF) yet. But I think from every early on, at least I need to have a place to test with everything together, without risk of breaking everything that others see. 


------


Between api.staging.tinybug.ai and staging.tinybug.ai/api (or apis), to be honest, I like staging.tinybug.ai/api. 

Similarly, I don't like app.tinybug.ai. I like a path under tinybug.ai (but I don't like tinybug.ai/app)

tinybug.ai/robinhood seems cool. tinybug.ai/orgs/robinhood is also fine. 


With these thoughts, can you recommend a URL strategy for me? 
I want it to cover:

- staging vs. prod (and later we might have dev.tinybug.ai, etc.)
- logged-out site vs. logged-in site
- multi tenancy
- serving pages for browsers vs. endpoint for APIs
