import pickle

fp = open('cache.dat', 'r')
words = pickle.loads(fp.read())
fp.close()

for word in words:
	print '%s -> %s' % (word, ', '.join(words))
