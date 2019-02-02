#!/usr/bin/env python3

import sys
from lib import opc                                                                                                                                                               
from time import sleep
from random import randint


class DataFlow:

    def __init__(self, num_leds=60, num_segments=3, brightness=.75, refresh=.1):

        self.num_leds = num_leds
        self.num_segments = num_segments
        self.brightness = brightness
        self.refresh = refresh
        self._stop = False

        self.client = opc.Client('localhost:7890')

        self.segments = []
        for s in range(num_segments):
            self.segments.append(self._make_segment())



    def start(self):

        while not self._stop:

            pixels = [(0,0,0)] * self.num_leds

            for segment in self.segments:

                segment_pos = segment.increment()

                for i in range(len(segment)):
                    pixel_pos = (segment_pos + i) % self.num_leds

                    new_pixel = segment[i]
                    old_pixel = pixels[pixel_pos]

                    pixels[pixel_pos] = self._merge_pixels(old_pixel, new_pixel)

                

            self.client.put_pixels(pixels[:self.num_leds])
            #print(pixels)
            sleep(self.refresh)


    def stop(self):

        self._stop = True
        sleep(self.refresh + .1)

        self.client.put_pixels( [(0,0,0)] * self.num_leds )



    def _make_segment(self, _min=1, _max=25):

        segment_length = randint(_min, _max)
        segment = Segment(length=segment_length, brightness=self.brightness)
        return segment


    @staticmethod
    def _merge_pixels(pixel1, pixel2):

        new_pixel = [0,0,0]

        for i in range(3):
            new_pixel[i] = min(255, max(0, int(pixel1[i] + pixel2[i])))

        return tuple(new_pixel)



class Segment(list):

    def __init__(self, length=10, brightness=.75, color=(0,1,0)):

        color = tuple([max(0, min(1, c)) for c in color])

        # length >= 1
        self.length = max(1, int(length))
        # 0.05 <= speed <= 1
        self.speed = max(.05, min(1, ( 2/self.length )))
        # 0 <= brightness <= 255
        self.brightness = max(0, min( 255, int( brightness * 255 * (1/self.length) ) ))

        # position
        self.pos = 0

        pixel = [0,0,0]

        for base in range(len(color)):
            if color[base] >= 0:
                pixel[base] = self.brightness * color[base]

        for i in range(self.length):
            self.append(tuple(pixel))


    def increment(self):

        self.pos += self.speed

        return int(self.pos)





if __name__ == '__main__':

    d = DataFlow()
    d.start()
    '''
    for i in [1, 10, 20, 30]:
        test = Segment(length=i)
        print('length', test.length)
        print('speed', test.speed)
        print('brightness', test.brightness)
        print(test)
        print('=' * 20)
    '''

    '''
    try:
        if len(sys.argv) <= 1:
            d.start()
    except Exception as e:
        print('[!] {}'.format(str(e)))
    finally:
        d.stop()
    '''