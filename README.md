# LunaRover
## Introduction
I have a dog named Luna. I sometimes feel bad when I leave Luna to entertain herself. I wanted a cool new project to work on. Considering all that, I present to you.... the LunaRover.

## What already exists?
If I wanted to leave my dog in the garden to entertain herself, what products could I procure to achieve that? And how do those products compare to the real deal of me being with Luna? For example, I can give her a stick - which she will play with, but its nothing like the fun she has when I chase her around my garden. To get an understanding of that I thought it'd be useful to present a venn diagram with buckets for: how I currently entertain my dog, what autonomous systems exist, and what powered vehicles exist. The listed items within each bucket are by no means exhaustive, but inspire idea generation nonetheless.

![Lit Review Venn](./venn.png)


It surprises me that I couldn't find evidence of someone having created an autonomous vehicle to play with their dog... that's something that I've sought to resolve.

## Proposed solution
Brushed motor radio controlled (rc) car modified to drive autonomously with the help of a raspberry pi.

## Method
### Step 1 - Understand how the rc car hand-me-down I got worked and retrofitting my own circuitry
I was fortunate enough to be given an rc car for free by my uncle. What's great about the rc car that I got is that it is really easy to understand what is going on, and it meets my torque requirements!

So.... how does it work? A radio transponder sends out a signal to a transceiver (mine was an acoms transceiver). The transceiver then interprets the signal and sends a Pulse Width Modulated (PWM) signal to one of two servos. The first servo controls direction of the front wheels, the second servo controls a mechanical speed controller - which is sort of like a potentiometer for scaling output voltage to the brushed dc motor driving the rear wheels. It's important to note that there is a Battery Eliminator Circuit (BEC) in the acoms receiver which enables the 7.2V from the battery to be stepped down to within the operating voltage range for servo motors.

So, easy right.... well, a bit, but not entirely. My servo motor was a hand-me-down, so naturally I was missing the transponder to control the rc car. So, I had to control the car another way... in the end I opted for a raspberry pi 5 - as I know I'd end up using it for the image detection later on. I stripped out the receiver and modified the circuitry slightly so that it looked like the below:

![Circuit Diagram](./circuit.PNG)

### Step 2 - Simulate desired logic with arduino
As this is the first time I've used a raspberry pi I thought it'd be a good idea to see how the logic performs with an Arduin, that I had to hand.

By considering the following logic, for drive and steering respectively, we can see how we can change the instruction given to the car.

* F when pin 1 is high and pin 2 is low the car moves forward, 
* B when pin 2 is high and pin 1 is low the car moves backwards, 

* R when pin 3 is high and pin 4 is low the car turns right,
* L when pin 4 is high and pin 3 is low the car turns left,
  
* N when all four pins are low - the car does move nor turn.

Therefore, if we feed into 2 characters to the serial port, e.g FR - for forward and right, we should be able to control the car using the arduino.

### Step 3 - Upload operating system to raspberry pi and emulate program for arduino (c++) into python
Logic is exactly the same as step 2, just written in python - to be used with my raspberry pi.

#### Step 4 - Remotely operate with raspberry pi
...Need boost converter so can use rc car provided batteries first, then should work a treat!

## Next Steps
* Make plan. What do I need? Thinking to 1. get rc car then modify so that can adjust output based on output from controller - which is connected to the Raspberry Pi 5, 2. position camera such that no motor output when grass is not identified in top quadrant of the screen (so stops at garden boundary) 3. such that movement is somewhat random but stops moving when senses object within close distance using lidar.
