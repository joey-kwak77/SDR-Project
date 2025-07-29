# create and send signals according to the target location
import numpy as np
from comms_lib.pluto import Pluto

class Pam:
    def __init__(self):
        pass

    def pam_constallation(self, N):
        """
        Generate a PAM constellation diagram for N levels. The average power of the constellation must be 1.

        Parameters:
        N (int): Number of PAM levels.

        Returns:
        list: A list of PAM levels.
        """
        if N <= 0:
            raise ValueError("Number of levels must be a positive integer.")

        #implement the PAM constellation generation logic
        pam_symbols = np.arange(-N+1, N, 2)
        
        s = np.sum(np.square(pam_symbols)) // N
        d = np.sqrt(1/s)
        pam_symbols = pam_symbols * d

        return pam_symbols


    def create_symbol(self, r: int, c: int):
        '''
        loc: r, c; both ints between 0 and 9 inclusive
        10 x 10 board --> M = 16, L = 4

        Returns: array of len 2 containing the symbols corresponding to each grid
        '''

        cons = self.pam_constallation(16)
        return np.array([cons[r], cons[c]])


    def create_message(self, symbols, K):
        '''
        K: number of repeats
        '''
        #make the square wave
        l = np.repeat(symbols, K)
        return l


    def decode_message(self, m, K, N):
        '''
        m: message
        K: number of repeats in m
        N: number of PAM levels
        return symbols
        '''
        L = np.log2(N)
        symb = []
        i = 0
        while i < len(m):
            symb.append(np.average(np.array(m[i:i+K])))
            i += K
        
        return symb


    def detect_pam_symbol(self, N, received_symbol):
        """
        Detect the PAM symbol from a received symbol.

        Parameters:
        N (int): Number of PAM levels.
        received_symbol (complex): The received symbol to be detected.

        Returns:
        complex: The detected PAM symbol.
        """
        #implement the PAM symbol detection logic
        cons = self.pam_constallation(N)
        res = []
        for s in received_symbol:
            s = np.real(s)
            dif = np.abs(np.array(cons - s))
            m = np.argmin(dif)
            res.append(cons[m])
        return res

    def get_loc(self, symbols):
        '''
        symbols: np.array of len 2
        N = 16

        Return: tuple location
        '''
        res = [-1,-1]
        cons = self.pam_constallation(16)
        for i in range(2):
            s = symbols[i]
            j = np.where(cons == s)[0][0]
            res[i] = j
        return res
