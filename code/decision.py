import numpy as np
from scipy import stats


# This is where you can build a decision tree for determining throttle, brake and steer 
# commands based on the output of the perception_step() function
def decision_step(Rover):

    # Implement conditionals to decide what to do given perception data
    # Here you're all set up with some basic functionality but you'll need to
    # improve on this decision tree to do a good job of navigating autonomously!

    # Example:
    # Check if we have vision data to make decisions with
    if Rover.nav_angles is not None:
        # Check for Rover.mode status
        if Rover.mode == 'forward': 
            # Check the extent of navigable terrain
            if len(Rover.nav_angles) >= Rover.stop_forward:  
                # If mode is forward, navigable terrain looks good 
                if Rover.vel < 0.2:
                    # Are we stuck? If we fail to achieve velocity for a sufficient
                    # number of samples, then assume we are stuck and force four wheel
                    # turning. The four wheel turning occurs for 20 samples
                    Rover.slow_samples += 1
                    if Rover.slow_samples > 50:
                        Rover.throttle = 0
                        #Rover.brake = Rover.brake_set
                        Rover.brake = 0
                        Rover.steer = -15
                        if Rover.slow_samples > 60:
                            Rover.throttle = -0.2
                            if Rover.slow_samples > 65:
                                Rover.slow_samples = 0
                        return Rover
                if Rover.vel >= 0.2:
                    Rover.slow_samples = 0
                if Rover.vel < Rover.max_vel:
                    # Set throttle value to throttle setting
                    Rover.throttle = Rover.throttle_set
                else: # Else coast
                    Rover.throttle = 0
                Rover.brake = 0
                # Set steering to average angle clipped to the range +/- 15
    
                # we have a clear path - is there a rock we can pursue - assume no obstacle
                if Rover.rock_angles is not None:
                    if Rover.vel < 0.2 and Rover.rock_dist >= Rover.vel*20:
                        Rover.throttle = 0.2
                    else:
                        Rover.throttle = 0
                    # apply some randomness to the approach so that if we fail the first time we might get it the second time
                    Rover.steer = np.clip(np.mean(Rover.rock_angles * 180/np.pi) + np.random.randint(-3,3), -15, 15) 
                    # when we are close enough, stop the rover so we can pick up the rock
                    if Rover.rock_dist < Rover.vel * 20:
                        Rover.throttle = 0
                        Rover.brake = Rover.brake_set
                        Rover.mode = 'stop'
                else:
                    # maintain a bias to keep ourselves close to the left canyon wall in order to do a
                    # better job exploring the canyon
                    deg_angles = Rover.nav_angles * 180/np.pi
                    mean_angle = np.mean(deg_angles)
                    Rover.steer = np.clip(np.clip(np.mean(deg_angles[deg_angles >= mean_angle]), -15, 15) + np.random.randint(-3,3),-15,15)
            # If there's a lack of navigable terrain pixels then go to 'stop' mode
            elif Rover.rock_angles is not None:
                Rover.throttle = 0
                Rover.steer = np.clip(np.mean(Rover.rock_angles * 180/np.pi), -15, 15) 
                if Rover.rock_dist < Rover.vel * 20:
                    Rover.throttle = 0
                    Rover.brake = Rover.brake_set
                    Rover.mode = 'stop'
            elif len(Rover.nav_angles) < Rover.stop_forward:
                    # Set mode to "stop" and hit the brakes!
                    Rover.throttle = 0
                    # Set brake to stored brake value
                    Rover.brake = Rover.brake_set
                    Rover.steer = 0
                    Rover.mode = 'stop'

        # If we're already in "stop" mode then make different decisions
        elif Rover.mode == 'stop':
            # If we're in stop mode but still moving keep braking
            if Rover.vel > 0.2:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
                Rover.consec_stop_frames = 0
                Rover.mode = 'forward'
            # If we're not moving (vel < 0.2) then do something else
            elif Rover.vel <= 0.2:
                # Now we're stopped and we have vision data to see if there's a path forward
                if len(Rover.nav_angles) < Rover.go_forward:
                    if Rover.rock_angles is not None:
                        # try to push forward to get your sample
                        if len(Rover.nav_angles) >= Rover.rock_forward:
                            Rover.throttle = 0.2
                            Rover.brake = 0
                            Rover.steer = np.clip(np.mean(Rover.rock_angles*180/np.pi), -15, 15)
                        else:
                            Rover.throttle = 0
                            Rover.brake = 0
                            Rover.steer = -15
                    else:
                        Rover.throttle = 0
                        # Release the brake to allow turning
                        Rover.brake = 0
                        Rover.steer = -15 # Could be more clever here about which way to turn
                # If we're stopped but see sufficient navigable terrain in front then go!
                if len(Rover.nav_angles) >= Rover.go_forward:
                    # remain in the stopped state if we don't actually have a forward path
                    if (np.mean(Rover.nav_angles) - 15) < 30:
                        # Set throttle back to stored value
                        Rover.throttle = Rover.throttle_set
                        # Release the brake
                        Rover.brake = 0
                        # Set steer to mean angle
                        if Rover.rock_angles is not None:
                            Rover.steer = np.clip(np.mean(Rover.rock_angles * 180/np.pi), -15, 15)
   
                            if Rover.rock_dist < 10:
                                Rover.throttle = 0
                                Rover.brake = Rover.brake_set
                                Rover.mode = 'stop'
                        else:
                            # maintain a bias to keep ourselves close to the left canyon wall in order to do a
                            # better job exploring the canyon
                            deg_angles = Rover.nav_angles * 180/np.pi
                            mean_angle = np.mean(deg_angles)
                            Rover.steer = np.clip(np.mean(deg_angles[deg_angles >= mean_angle]), -15, 15)
                            
                        Rover.mode = 'forward'
    # Just to make the rover do something 
    # even if no modifications have been made to the code
    else:
        Rover.throttle = Rover.throttle_set
        Rover.steer = 0
        Rover.brake = 0
        
    # If in a state where want to pickup a rock send pickup command
    if Rover.near_sample and Rover.vel == 0 and not Rover.picking_up:
        Rover.send_pickup = True
    
    return Rover

