#!/usr/bin/env python3

# by TheTechromancer

import sys
from lib import opc                                                                                                                                                               
from time import sleep
from random import randint

### DEFAULTS ###

num_leds = 240
num_segments = int(num_leds / 3)



### CLASSES ###

class DataFlow:

    def __init__(self, num_leds=60, num_segments=10, brightness=1, refresh=.05, direction=-1):

        self.num_leds = num_leds
        self.num_segments = num_segments
        self.brightness = min(1, max(0, brightness))
        self.refresh = refresh
        
        assert direction in (1, -1), '"direction" must be either 1 or -1'
        self.direction = direction

        self._stop = False

        self.client = opc.Client('localhost:7890')

        self.segments = list(self._make_segments())

        # randomize starting positions
        for segment in self.segments:
            segment.pos = randint(0, self.num_leds)



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


            pixels = pixels[:self.num_leds][::self.direction]
            self.client.put_pixels(pixels)
            #print([p[1] for p in pixels])
            sleep(self.refresh)


    def stop(self):

        self._stop = True
        sleep(self.refresh + .1)

        self.client.put_pixels( [(0,0,0)] * self.num_leds )



    def _make_segments(self, _min=1, _max=30):

        segment_length = int(_min)
        for i in range(self.num_segments):
            segment = Segment(length=int(segment_length), brightness=self.brightness)
            segment_length = min(_max, max(_min, segment_length + (_max / self.num_segments)) )
            yield segment



    def _merge_pixels(self, pixel1, pixel2):

        new_pixel = [0,0,0]

        for i in range(3):
            new_pixel[i] = int( min((self.brightness*255), max(0, pixel1[i] + pixel2[i])) )

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
                pixel[base] = int(self.brightness * color[base])

        for i in range(self.length):
            self.append(tuple(pixel))


    def increment(self):

        self.pos += self.speed

        return int(self.pos)





if __name__ == '__main__':

    d = DataFlow(num_leds=num_leds, num_segments=num_segments)
    '''
    for i in [1, 10, 20, 30]:
        test = Segment(length=i)
        print('length', test.length)
        print('speed', test.speed)
        print('brightness', test.brightness)
        print(test)
        print('=' * 20)
    '''

    try:
        if len(sys.argv) <= 1:
            d.start()
    except Exception as e:
        print('[!] {}'.format(str(e)))
    finally:
        d.stop()
