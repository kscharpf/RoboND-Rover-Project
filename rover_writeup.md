## Project: Search and Sample Return

---


**The goals / steps of this project are the following:**  

**Training / Calibration**  

* Download the simulator and take data in "Training Mode"
* Test out the functions in the Jupyter Notebook provided
* Add functions to detect obstacles and samples of interest (golden rocks)
* Fill in the `process_image()` function with the appropriate image processing steps (perspective transform, color threshold etc.) to get from raw images to a map.  The `output_image` you create in this step should demonstrate that your mapping pipeline works.
* Use `moviepy` to process the images in your saved dataset with the `process_image()` function.  Include the video you produce as part of your submission.

**Autonomous Navigation / Mapping**

* Fill in the `perception_step()` function within the `perception.py` script with the appropriate image processing functions to create a map and update `Rover()` data (similar to what you did with `process_image()` in the notebook). 
* Fill in the `decision_step()` function within the `decision.py` script with conditional statements that take into consideration the outputs of the `perception_step()` in deciding how to issue throttle, brake and steering commands. 
* Iterate on your perception and decision function until your rover does a reasonable (need to define metric) job of navigating and mapping.  

[//]: # (Image References)

[image1]: ./misc/rover_image.jpg
[image2]: ./calibration_images/example_grid1.jpg
[image3]: ./calibration_images/example_rock1.jpg 
[image4]: ./output/example_grid_warped.jpg
[image5]: ./output/example_rock_warped.jpg
[image6]: ./output/example_grid_mask.jpg
[image7]: ./output/example_grid_ground.jpg
[image8]: ./output/example_grid_obstacles.jpg
[image9]: ./output/example_grid_samples.jpg
[image10]: ./output/example_rock_ground.jpg
[image11]: ./output/example_rock_obstacles.jpg
[image12]: ./output/example_rock_samples.jpg


## [Rubric](https://review.udacity.com/#!/rubrics/916/view) Points
### Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

---
### Writeup / README

#### 1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  

You're reading it!

### Notebook Analysis
#### 1. Run the functions provided in the notebook on test images (first with the test data provided, next on data you have recorded). Add/modify functions to allow for color selection of obstacles and rock samples.

Example grid and example rock images:
![alt text][image2]
![alt text][image3]

Warped perspective of the two example images:
![alt text][image4]
![alt text][image5]

I used the field of view masking technique provided in the project overview video rather than simply negating the navigable terrain. The masked field of view looks identical regardless of source image.
![alt text][image6]

To identify the navigable terrain versus obstacles versus rocks, I updated the color_thresh function provided during the classwork to take a range of RGB values rather than a single low threshold. The identification of an obstacle is those areas within the FOV mask that are identified as not navigable. For the samples, there is a low amount of blue present in pixels for the samples. Here are the navigable terrain, obstacles, and rock for the example_grid file provided:
![alt text][image7]
![alt text][image8]
![alt text][image9]

There is no rock in the example_grid image so the all-black presentation is as expected. Now here are the images produced for navigable, obstacles, and rock for example_rock image:

![alt text][image10]
![alt text][image11]
![alt text][image12]

Here you see the small blip of white indicating pixels that passed the rock samples filter in the bottom center of the image.

#### 1. Populate the `process_image()` function with the appropriate analysis steps to map pixels identifying navigable terrain, obstacles and rock samples into a worldmap.  Run `process_image()` on your test data using the `moviepy` functions provided to create video output of your result. 


### Autonomous Navigation and Mapping

#### 1. Fill in the `perception_step()` (at the bottom of the `perception.py` script) and `decision_step()` (in `decision.py`) functions in the autonomous mapping scripts and an explanation is provided in the writeup of how and why these functions were modified as they were.

The perception_step implemented looks substantially similar to the process_image function. I used the same source/destination for perspective transform as was used in the lab. The Rover.vision_image was updated as in the overview video. To improve the fidelity of the map, the updates to the world_map are only done when both the roll and the pitch are less than 1deg absolute value.

I made a few significant changes to the decision_step() processing. First, I noted there was a propensity for the rover to get stuck in a condition where the obstacle is out of view of the camera. Here, I deal with that by noting that some number of samples have been seen (I chose 100) with a clear path ahead but the velocity is still less than 0.2. In such a situation, I stop the robot and force the four wheel turning for 20 samples. Relatedly, I noted that the rover would sometimes falsely consider the forward progress possible when already stopped. In this case, I find that although there are plenty of navigable pixels in my field of view, all of those angles are outside of the -15 to +15 steering range of the rover. In this case, I want to continue behaving as if I need to do four wheel turning. With these changes in place the rover no longer gets stuck in place.

I modified the rover to support picking up of samples. When a sample is present in the field of view and the path forward is available, I steer the rover towards the center of the sample. In order to attempt to avoid rolling past the samples, once the rover has gotten close to the samples I apply the brakes. This logic is not foolproof. Mainly, the rover often has the sample exit the field of view and the rover has no memory that it was in the field of view and thus continues onward.

Finally, I noted that even with the changes to prevent the rover from getting stuck in place, I noticed that my area mapping was often too low. The situation is that the rover is in a fairly wide open space. In such a situation, the rover's navigation logic of choosing the mean navigable angle results in circular motion. The idea I had to deal with that was to try to get the rover to follow alongside a wall. In order to do this, I decided to follow the angle corresponding to the third quartile of the navigable angles. I did this by taking the mean of all of the navigable angles that are greater than the mean angle. With this logic change, left to run the mapping exceeds 98%.

#### 2. Launching in autonomous mode your rover can navigate and map autonomously.  Explain your results and how you might improve them in your writeup.  

**Note: running the simulator with different choices of resolution and graphics quality may produce different results, particularly on different machines!  Make a note of your simulator settings (resolution and graphics quality set on launch) and frames per second (FPS output to terminal by `drive_rover.py`) in your writeup when you submit the project so your reviewer can reproduce your results.**

I executed my tests using the "Good" graphics quality and 1024x768 resolution and 14FPS. My platform is Ubuntu 17.10 on a Dell XPS13 with the Core I7 processor. Here are the results at different timesteps:

Time: Collected/Located Mapped Fidelity
60s: 0/0 13% 55%
120s: 0/0 18% 55%
180s: 0/0 18% 55%
240s: 0/0 45% 64%
300s: 1/1 47% 63%
360s: 1/1 58% 66%
420s: 1/1 61% 65%
480s: 1/1 68% 66%
540s: 1/2 78% 68%
600s: 1/2 80% 66%
660s: 1/4 94% 67%
720s: 2/4 95% 66%
780s: 2/5 96% 66%
840s: 2/5 96% 65%
900s: 2/5 96% 65% (simulation terminated)

There are several areas for improvement here. The most obvious is that between 60s and 180s there was only 5% additional terrain mapped. The reason was that the particular start location resulted in a loop through an open area. Any logic that takes into account history and unexplored areas would do better. A similar problem happens after 720s. At that time, there are two objects at different places in the canyon and the approach logic fails to collect the objects each time. A better approach logic or if the rover had some memory that it was going after a sample would do better. Finally, I did not attempt to add in the necessary logic for the rover to return to the start to deliver the supplies.
