import os, sys, pickle, random, json
import requests as req

API_BASE = "http://api.wordnik.com:80/v4/"
wordcache = {}

# CACHE FUNCTIONALITY
# Since API calls are expensive for everyone involved, and there's probably
# a lot of words that appear more than once in a corpus, we implement a cache here.
# To make it persistent, we save it between runs. Chances are after enough runs, your
# cache will be full enough to have very few cache misses on a small text with
# common enough words.
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
	if word in wordcache.keys():
		return random.choice(wordcache[word])
	else:
		# get a synonym for the word and choose at random.
		payload = { 'word':word, 'useCanonical':False, 'relationshipTypes':'synonym', 'limitPerRelationshipType':10 }
		r = req.get(API_BASE + '/word.json/' + word + '/relatedWords', data = json.dumps(payload))
		r.raise_for_status()
		defs = json.loads(r.json())
		if len(defs) < 1:
			return None # I assume, use the original word?
		else:
			words_list = defs[0]['words']
			# once you've retrieved the word, cache it for later.
			add_synonyms_to_cache(word, words_list)
			return random.choice(words_list)

def confuse_tokens(corpus_tokens):
	out = []
	for token in corpus_tokens:
		alt = fetch_word_alternative(token)
		if alt is not None:
			out.append(alt) # use the synonym
		else:
			out.append(token) # no synonym for this word existed, so whatever
	return out

def main():
	if len(sys.argv) < 2:
		print 'Usage: %s {corpus}' % sys.argv[0]
		sys.exit(1)
	fp = open(sys.argv[1], 'r')
	fp.close() # TODO: make better
	# just load the word cache since we'll need it
	if os.path.exists('cache.dat'):
		prepopulate_runtime_cache('cache.dat')

	# TODO: login

	sentence = ['my', 'stevedore', 'has', 'a', 'first', 'name', "it's", "OSCAR"]
	confused_sentence = confuse_tokens(sentence)
	print 'Original %s' % " ".join(sentence)
	print 'Twisted! %s' % " ".join(confused_sentence)

	# we're done here, so write the cache back out
	write_runtime_cache('cache.dat')

if __name__ == '__main__': main()
