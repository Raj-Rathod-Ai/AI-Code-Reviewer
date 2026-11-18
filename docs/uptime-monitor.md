# Keep the Render web service responsive

This project already serves `GET /` from its FastAPI app. Use that existing URL as the health-check target; no application or backend code changes are needed.

## Configure an external uptime monitor

The monitor must run outside this Render web service. A loop started inside the same free web service cannot keep that service awake because it will stop when the service spins down.

1. Create an account with an external uptime-monitoring provider such as [UptimeRobot](https://uptimerobot.com/).
2. Add a new **HTTP(s)** monitor.
3. Set the URL to:

   `https://ai-code-reviewer-jqh4.onrender.com/`

4. Choose the shortest polling interval available on your monitor plan (for example, 5 minutes if offered).
5. Save the monitor and confirm that it reports the endpoint as **Up**.

## What this does and does not guarantee

- The monitor periodically sends an ordinary HTTP request to the app's existing homepage.
- It does not require a new Python process, a background worker, a new dependency, or changes to `app.py`.
- External pings may reduce idle spin-downs, but they are not a guarantee of 24/7 availability. Render's free-service policies and platform behavior can still cause a service to spin down or restart.
- For guaranteed always-on service behavior, use a Render plan that includes always-on instances.

## Health-check target

- Method: `GET`
- Path: `/`
- URL: `https://ai-code-reviewer-jqh4.onrender.com/`

The existing homepage is used deliberately so this setup does not alter the working backend.
