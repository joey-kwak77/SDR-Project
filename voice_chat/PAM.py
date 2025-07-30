# create and send signals according to the target location
import numpy as np

class Pam:
    def __init__(self):
        pass

    def pam_constallation(self, N):
        """
        Generate a PAM constellation diagram for N levels. The average power of the constellation must be 1.

        Parameters:
        N (int): Number of PAM levels.          should be 4!!

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


    def digital_modulation(self, bits: list, N: int):
        '''
        maps bits to symbols

        Parameters:
        bits (list): a list of bits representing the audio recording
        N (int): Number of PAM levels.          should be 4!!

        Returns:
        res (list): a list of symbols each 8 bits map to
        '''

        cons = self.pam_constallation(N)
        res = []
        for num in bits:
            n1 = num[:len(num)//4]
            n2 = num[len(num)//4:len(num)//2]
            n3 = num[len(num)//2:(len(num)//4) *3]
            n4 = num[(len(num)//4)*3:]

            res.append(float(cons[int(n1, 2)]))
            res.append(float(cons[int(n2, 2)]))
            res.append(float(cons[int(n3, 2)]))
            res.append(float(cons[int(n4, 2)]))

        return res


    def create_message(self, symbols, K):
        '''
        Parameters:
        symbols: a list of symbols
        K: number of repeats
        '''
        #make the square wave
        l = np.repeat(symbols, K)
        return l


    def decode_message(self, m, K, N):
        '''
        Parameters:
        m: message
        K: number of repeats in m
        N (int): Number of PAM levels.          should be 4!!

        Returns:
        symb: the symbols decoded
        '''
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
        N (int): Number of PAM levels.          should be 4!!
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


    def symbol_to_bits(self, N, symbols):
        '''
        Parameters:
        N (int): Number of PAM levels.          should be 4!!
        symbols: recieved symbols

        Returns:
        res (list): corresponding bits to each symbol
        '''
        L = int(np.log2(N))
        zeros = "0" * L
        M = 2**L
        cons = self.pam_constallation(N)
        res = []
        i = 0
        for s in symbols:
            if i % 4 == 0:
                num = ""
            j = np.where(cons == s)[0][0]
            b = bin(j)[2:]
            l = L - len(b)
            num += zeros[:l]
            num += b
            if i % 4 == 3:
                res.append(num)
            i += 1
        return res
