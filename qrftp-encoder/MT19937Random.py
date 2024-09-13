# Derived from https://github.com/yinengy/Mersenne-Twister-in-Python/blob/master/RandomClass.py

# MIT License

# Copyright (c) 2019 yinengy

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

class MT19937Random():
    def __init__(self, c_seed=0):
        # MT19937
        (self.w, self.n, self.m, self.r) = (32, 624, 397, 31)
        self.a = 0x9908B0DF
        (self.u, self.d) = (11, 0xFFFFFFFF)
        (self.s, self.b) = (7, 0x9D2C5680)
        (self.t, self.c) = (15, 0xEFC60000)
        self.l = 18
        self.f = 1812433253
        # make a arry to store the state of the generator
        self.MT = [0 for i in range(self.n)]
        self.index = self.n+1
        self.lower_mask = 0x7FFFFFFF
        self.upper_mask = 0x80000000
        # inital the seed
        self.c_seed = c_seed
        self.seed(c_seed)

    def seed(self, num):
        """initialize the generator from a seed"""
        self.MT[0] = num
        self.index = self.n
        for i in range(1, self.n):
            temp = self.f * (self.MT[i-1] ^ (self.MT[i-1] >> (self.w-2))) + i
            self.MT[i] = temp & 0xffffffff

    def twist(self):
        """ Generate the next n values from the series x_i"""
        for i in range(0, self.n):
            x = (self.MT[i] & self.upper_mask) + \
                (self.MT[(i+1) % self.n] & self.lower_mask)
            xA = x >> 1
            if (x % 2) != 0:
                xA = xA ^ self.a
            self.MT[i] = self.MT[(i + self.m) % self.n] ^ xA
        self.index = 0

    def extract_number(self):
        """ Extract a tempered value based on MT[index]
            calling twist() every n numbers
        """
        if self.index >= self.n:
            self.twist()

        y = self.MT[self.index]
        y = y ^ ((y >> self.u) & self.d)
        y = y ^ ((y << self.s) & self.b)
        y = y ^ ((y << self.t) & self.c)
        y = y ^ (y >> self.l)

        self.index += 1
        return y & 0xffffffff

    def sample(self, n, k):
        """ Sample k numbers from range 0 ... n-1
        """
        arr = [i for i in range(n)]
        samples = []
        for _ in range(k):
            idx = self.extract_number() % len(arr)
            samples.append(arr[idx])
            del arr[idx]
        return samples
