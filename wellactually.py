import sys, pickle

API_BASE = "http://api.wordnik.com:80/v4/"
wordcache = {}

def prepopulate_runtime_cache(filename):
	global wordcache # make sure we know that the write is not a local variable
	# load a word cache from file
	infile = open(filename, 'r')
	wordcache = pickle.load(infile)
	infile.close()

def write_runtime_cache(filename):
	out = open(filename, 'w')
	pickle.dump(wordcache, out)
	out.close()
	
def add_synonyms_to_cache(base_word, synonyms):
	for synonym in synonyms:
		add_word_to_cache(base_word, synonym)
		add_word_to_cache(synonym, base_word) # synonyms are bidirectional.

def add_word_to_cache(base_word, synonym):
	# check if word exists in dict
	# 	if not exists in dict, make new list with only synonym
	# else, append
	#	if word already in list, dump it.
	if not base_word in wordcache.keys():
		wordcache[base_word] = [synonym]
	else:
		if not synonym in wordcache[base_word]:
			wordcache[base_word].append(synonym)
			

def fetch_word_alternative(word):
	# get a synonym for the word and choose at random.
	# once you've retrieved the word, cache it for later.
	# TODO: what would be a smart way to go 'backward' (if they retrieved a -> b, don't go up to the network for b -> a)?
	print 'no fetching yet TODO'

def main():
	if len(sys.argv) < 2:
		print 'Usage: %s {corpus}' % sys.argv[0]
		sys.exit(1)
	fp = open(sys.argv[1], 'r')
	fp.close() # TODO: make better
	# just load the word cache since we'll need it
	if os.path.exists('cache.dat'):
		prepopulate_runtime_cache('cache.dat')

	# we're done here, so write the cache back out
	write_runtime_cache('cache.dat')

if __name__ == '__main__': main()
