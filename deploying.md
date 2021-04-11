# Deploy covid-vaccine-notifier

Here are some ways to deploy the covid-vaccine-notifier script. If you do it a different way, I would welcome a PR to this file describing how to do it so others can benefit!

## On-prem machine

If you have a computer on all the time, all you need to do is [run the script](README.md#running) and keep it running while you want notifications.


## AWS

TBD

## Saturn Cloud

[Saturn Cloud](https://saturncloud.io) is a cloud-based platform for setting up and running Python data science projects (disclaimer: Saturn Cloud is my employer). There is a free tier where you can have a few hours per month of resources running, or pay by usage if you exceed that. 

To have this script running all the time, create a new project and clone the repo into it. Then, set up a [Deployment](https://www.saturncloud.io/docs/getting-started/jobs_and_deployments/#deployments) with the [Python script](README.md#running).

