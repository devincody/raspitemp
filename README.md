# Raspberry Pi Temperature monitor

Lowering my AC electric bill the hard way...

## What does it do

As part of making my home smarter, I wanted a way to manage the temperature in my appartment during the hot Pasadena summers. The code monitors the indoor and outdoor temperatures using two temperature probes and controlls a window fan using [IFTTT](ifttt.com) webhooks. This is the culmination of ~20 hours of work.

## What it really didn't need to do

I also added a bunch of completely unecessary functionality that was nevertheless pretty cool to do

### Custom hardware
Because perf board is ugly:
https://circuitmaker.com/Projects/Details/Devin-Cody/Raspberry-Pi-Zero-Hat-Temperature-probe

### OLED
The temperatures are continuously displayed on an I2C OLED display module

### Data Collection

Because I am a data nerd. The temperature data is stored and periodically plotted and sent to my desktop. The data window is selectable. The plotting code is included in this dirctory. See the example cron file for setting up automatic plotting and copying.



## Parts
* temperature Probes:
  - https://www.amazon.com/gp/product/B07DVJ1JHP/ref=ppx_yo_dt_b_asin_title_o03_s00?ie=UTF8&psc=1
* Fan:
  - https://www.amazon.com/gp/product/B001R1RXUG/ref=ppx_yo_dt_b_asin_title_o05_s00?ie=UTF8&psc=1
* Display:
  - https://www.amazon.com/gp/product/B079BN2J8V/ref=ppx_yo_dt_b_asin_title_o02_s00?ie=UTF8&psc=1
