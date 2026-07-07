# AENS Website

Investor site, technology deep-dive, and interactive product simulation for the Atmospheric Energy Navigation System (AENS): open source flight software that lets electric aircraft harvest atmospheric energy.

## Pages

- `index.html` : investor-facing overview, economics, and live ROI calculator
- `technology.html` : physics derivations, architecture, sensors, prior flight demonstrations, confidence levels
- `dashboard.html` : interactive mission-console simulation (AENS aircraft vs conventional aircraft on the same battery)

## Stack

Static HTML/CSS/JS. No build step, no dependencies. `vercel.json` enables clean URLs.

## Deploy

Import this repository at vercel.com/new. Framework preset: Other. No build command, output directory: root. Every push to `main` auto-deploys.

## License

Site content and code: Apache-2.0.
