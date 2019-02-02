#!/usr/bin/env python3

import sys
from lib import opc                                                                                                                                                               
from time import sleep
from random import randint


class Matrix:

    def __init__(self, num_leds=240, brightness=.8, refresh=.3):

        self.num_leds = num_leds
        self.brightness = brightness
        self.refresh = refresh
        self._stop = False

        self.client = opc.Client('localhost:7890')

        self.wheel = []
        while len(self.wheel) < self.num_leds:
            self.wheel += self._make_segment()
        self.wheel = self.wheel[::-1]


    def start(self):


        pixels = self.wheel[:self.num_leds]
        start_pixel = 0

        while not self._stop:

            for j in range(self.num_leds):
                pixels[-(j+1)] = self.wheel[(j+start_pixel) % len(self.wheel)]

            self.client.put_pixels(pixels[:self.num_leds])
            sleep(self.refresh)

            start_pixel += 1


    def stop(self):

        self._stop = True
        sleep(self.refresh + .1)

        self.client.put_pixels( [(0,0,0)] * self.num_leds )



    def _make_segment(self, _min=10, _max=25):

        segment_length = randint(_min, _max)

        segment = [(0, int((k*(256/(segment_length+1)) * self.brightness)), 0) for k in range(segment_length)]

        return segment



if __name__ == '__main__':

    m = Matrix()

    try:
        if len(sys.argv) <= 1:
            m.start()
    except Exception as e:
        print('[!] {}'.format(str(e)))
    finally:
        m.stop()