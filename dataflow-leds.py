#!/usr/bin/env python3

# by TheTechromancer

import sys
from lib import opc
from time import sleep
from random import randint
from statistics import mean

### DEFAULTS ###

num_leds = 420
num_segments = int(num_leds / 2.5)



### CLASSES ###

class DataFlow:

    def __init__(self, num_leds=60, num_segments=10, scale=1, brightness=1, refresh=.05, direction=-1):

        self.num_leds = num_leds
        self.num_upscaled_leds = int(num_leds * scale)
        # multiplier for internally-rendered strip, which is then downscaled
        self.scale = scale
        self.num_segments = num_segments
        self.brightness = min(1, max(0, brightness))
        self.refresh = refresh
        
        assert direction in (1, -1), '"direction" must be either 1 or -1'
        self.direction = direction

        self.STOP = False

        self.client = opc.Client('localhost:7890')

        self.segments = list(self._make_segments())



    def start(self):

        while not self.STOP:

            # upscaled pixels
            pixels = [(0,0,0)] * self.num_upscaled_leds

            # for every segment
            for segment in self.segments:

                # increment segment's position
                segment_pos = segment.increment()

                # for every pixel in this segment
                for i in range(len(segment)):
                    pixel_pos = (segment_pos + i) % self.num_upscaled_leds

                    new_pixel = segment[i]
                    old_pixel = pixels[pixel_pos]

                    # add it to the strip pixel in that position
                    pixels[pixel_pos] = self._add_pixels(old_pixel, new_pixel)


            pixels = pixels[:self.num_upscaled_leds][::self.direction]
            pixels = self._downscale_pixels(pixels)
            self.client.put_pixels(pixels)
            sleep(self.refresh)


    def stop(self):

        self.STOP = True
        sleep(self.refresh + .1)

        self.client.put_pixels( [(0,0,0)] * self.num_leds )



    def _make_segments(self, _min=1, _max=30):

        segment_length = int(_min)
        for i in range(self.num_segments):
            segment = Segment(length=int(segment_length), brightness=self.brightness, scale=self.scale)
            segment_length = min(_max, max(_min, segment_length + (_max / self.num_segments)) )
            # randomize starting position
            segment.pos = randint(0, self.num_upscaled_leds)
            yield segment



    def _add_pixels(self, pixel1, pixel2):

        new_pixel = [0,0,0]

        for i in range(3):
            new_pixel[i] = int( min(255, min((self.brightness*255), max(0, pixel1[i] + pixel2[i]))) )

        return tuple(new_pixel)


    def _downscale_pixels(self, pixels):

        scale = len(pixels) / self.num_leds
        new_pixels = []

        for i in range(self.num_leds):
            start_pixel = int(i * scale)
            end_pixel = int((i * scale) + scale)

            # take the color average of the pixel segment
            mean_r = int(mean([c[0] for c in pixels[start_pixel:end_pixel]]))
            mean_g = int(mean([c[1] for c in pixels[start_pixel:end_pixel]]))
            mean_b = int(mean([c[2] for c in pixels[start_pixel:end_pixel]]))

            new_pixels.append((mean_r, mean_g, mean_b))

        return new_pixels




class Segment(list):

    def __init__(self, length=10, brightness=.75, color=(0,1,0), scale=1):

        color = tuple([max(0, min(1, c)) for c in color])

        # length >= 1
        self.length = max(1, int(length * scale))
        # 0.05 <= speed <= 1
        self.speed = max(.05*scale, min(scale, ( scale/self.length )))
        # 0 <= brightness <= 255
        self.brightness = max(0, min( 255, int( brightness * 255 * (scale/self.length) ) ))

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

    try:
        if len(sys.argv) <= 1:
            d.start()
    except KeyboardInterrupt:
        print('[!] Interrupted')
    finally:
        d.stop()
