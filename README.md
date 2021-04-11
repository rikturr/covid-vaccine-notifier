# covid-vaccine-notifier

Python script that sends an email when a COVID-19 vaccine appointment is available near you!

Data comes from [vaccinespotter.org](https://vaccinespotter.org) by [Nick Muerdter](https://github.com/GUI). This script runs a [Prefect](https://github.com/PrefectHQ/prefect) flow that checks for nearby appointments every X minutes and sends an email when some are available.

I built this to find an appointment for myself, because the appointments were going and opening up so quickly, I found that even checking the website every couple of hours wasn't cutting it. I set this script up to check every 10 minutes and ended up finding a slot within a day! 

I'd like to make this easier to configure and perhaps re-factor it to check and send notifications for multiple people. For now, running the flow will check for one set of coordinates and send a notification to one email address that you need to add credentials for. If you want to run it yourself, clone the repo and follow the setup below!

## Setup

Several environment variables need to be set. Here is an example:

```bash
STATE=FL # 2-letter abbreviation of the state you are in
LATITUDE=25.7617
LONGITUDE=-80.1918
DISTANCE_MILES=100 # How far away you want to find appointments (in miles)
EMAIL=me@me.com # Email address to send notifications to
INTERVAL_MINUTES=10  # How often (in minutes) to check appointments
PREFECT__CONTEXT__SECRETS__EMAIL_PASSWORD= # see below
PREFECT__CONTEXT__SECRETS__EMAIL_USERNAME= # see below
```

An easy way to find your latitude/longitude is from this website: https://www.gps-coordinates.net/my-location.

The script uses an [EmailTask](https://docs.prefect.io/api/latest/tasks/notifications.html#emailtask) from Prefect, which requires a username and password. Per Prefect, its recommended to use a [Google App Password](https://support.google.com/accounts/answer/185833) if you use Gmail. One way to set these is by the environment variables provided above, but if you have a different Prefect setup you could set the [Secrets](https://docs.prefect.io/orchestration/concepts/secrets.html) another way.

A neat trick if you want text message updates is to utilize your cell phone provider's domain (more details [here](https://smith.ai/blog/how-send-email-text-message-and-text-via-email)):

- AT&T: phonenumber@txt.att.net
- T-Mobile: phonenumber@tmomail.net
- Sprint: phonenumber@messaging.sprintpcs.com
- Verizon: phonenumber@vtext.com or phonenumber@vzwpix.com
- Virgin Mobile: phonenumber@vmobl.com

## Running

To make sure you have all the right Python packages, create a virtual environment:

```bash
conda env create -f environment.yml
conda activate vaccine-appts
```

Make sure to set your environment variables (see above), then run the script!

```bash
python vaccine-appts.py
```

If you see the following message, then its working! The flow will run at the end of the interval period.

```bash
[2021-04-11 23:16:47+0000] INFO - prefect.covid-vaccine-appt-notifier | Waiting for next scheduled run at 2021-04-11T23:20:00+00:00
```

An email notification only gets sent out if appointments are found, otherwise you will see this message in the logs:

```bash
[2021-04-11 23:26:00+0000] INFO - prefect.TaskRunner | No appointments found :(
```

## Deploying

Ideally you would want this running all the time, because COVID vaccine appointment availability changes really fast. If you have a computer always-on at home that will work, or you could deploy it in the cloud.

Check out [deploying.md](deploying.md) for details on some deployment options. 

## Acknowledgements

- This project would not be possible without the major work done by [Nick Muerdter](https://github.com/GUI) for [vaccinespotter.org](https://vaccinespotter.org). 
- Thanks to [Saturn Cloud](https://saturncloud.io) (my employer) for access to the platform for building and running the flow.