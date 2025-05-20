from gpiozero import LED, Button, DigitalInputDevice
from signal import pause
import signal
import sys
from kubernetes import client, config
from pprint import pprint

import curses
from matrix_effect import matrix_effect

ARMED = False
TRIGGERED = False


def signal_handler(sig, frame):
    curses.endwin()
    sys.exit(0)


def main():
    # arm_btn = Button(4)
    arm_switch = DigitalInputDevice(4)
    trigger_btn = Button(18)
    green_led = LED(6)
    red_led = LED(12)

    def kill_switch():
        # Add check if already triggered to stop the animation from repeating on multiple button presses
        global TRIGGERED
        if not TRIGGERED:
            TRIGGERED = True
            curses.wrapper(matrix_effect)


    def dummy_switch():
        pass

    def toggle_armed_state():
        global ARMED, TRIGGERED
        ARMED = not ARMED
        green_led.toggle()
        red_led.toggle()

        if ARMED:
            trigger_btn.when_released = kill_switch
        else:
            # When disarmed, reset value of TRIGGERED => allows to run the detination again
            TRIGGERED = False
            trigger_btn.when_released = dummy_switch


    # setup inital state: Green 1, Red 0
    
    green_led.toggle()
    trigger_btn.when_released = dummy_switch
    arm_switch.when_activated = toggle_armed_state
    arm_switch.when_deactivated = toggle_armed_state
    arm_switch.wait_for_active()

    pause()


if __name__ == "__main__":
    # Set up a signal handler to handle interrupts
    signal.signal(signal.SIGINT, signal_handler)

    # Configs can be set in Configuration class directly or using helper utility
    config.load_kube_config()
    ctx = config.list_kube_config_contexts()
    pprint(ctx)


    v1 = client.CoreV1Api()
    # api_response = v1.read_namespaced_deployment('job-service', 'default', pretty=True)
    api_response = v1.delete_namespaced_service(name='job-service', namespace='default', pretty=True, dry_run='All', propagation_policy='Foreground')

    main()
    
    pprint(api_response)

