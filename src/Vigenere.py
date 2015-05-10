#	Copyright (c) 2014, Andrea Esposito <info@andreaesposito.org>
#	All rights reserved.
#
#	Redistribution and use in source and binary forms, with or without
#	modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the Andrea Esposito nor the
#      names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.
#
#	THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#	ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#	WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#	DISCLAIMED. IN NO EVENT SHALL Andrea Esposito BE LIABLE FOR ANY
#	DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#	(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#	LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#	ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#	(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#	SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

def encryptMessage(key, message):
    return translateMessage(key, message, 'encrypt')


def decryptMessage(key, message):
    return translateMessage(key, message, 'decrypt')


def translateMessage(key, message, mode):
	LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
	translated = [] # stores the encrypted/decrypted message string

	keyIndex = 0

	for symbol in message: # loop through each character in message
		num = LETTERS.find(symbol)
		if num != -1: # -1 means symbol was not found in LETTERS
			if mode == 'encrypt':
				num += LETTERS.find(key[keyIndex]) # add if encrypting
			elif mode == 'decrypt':
				num -= LETTERS.find(key[keyIndex]) # subtract if decrypting

			num %= len(LETTERS) # handle the potential wrap-around

			translated.append(LETTERS[num])

			keyIndex += 1 # move to the next letter in the key
			if keyIndex == len(key):
				keyIndex = 0
		else:
            # The symbol was not in LETTERS, so add it to translated as is.
			translated.append(symbol)

	return ''.join(translated)