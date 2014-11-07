import os, sys, pickle, random, json
import yaml
import requests as req

API_BASE = "http://api.wordnik.com:80/v4"
API_KEY = ""
DO_NOT_TRANSLATE = []
BAD_RESULTS = []
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
		if not synonym in BAD_RESULTS:
			add_word_to_cache(base_word, synonym)
			add_word_to_cache(synonym, base_word) # synonyms are bidirectional.
		else:
			print 'rejected ' + synonym

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
	if word in DO_NOT_TRANSLATE:
		return word	# leave it.

	(word, punct) = remove_punctuation(word)

	if word in wordcache.keys():
		return transform_output_word(random.choice(wordcache[word]), punct)
	else:
		# get a synonym for the word and choose at random.
		params = { 'word': word, 'useCanonical': False, 'relationshipTypes': 'synonym', 'limitPerRelationshipType': 10, 'api_key': API_KEY }
		url = API_BASE + '/word.json/' + word + '/relatedWords'
		r = req.get(url, params = params)
		r.raise_for_status()
		defs = r.json()
		if len(defs) < 1:
			return None # I assume, use the original word?
		else:
			words_list = defs[0]['words']
			# once you've retrieved the word, cache it for later.
			add_synonyms_to_cache(word, words_list)
			# offer a fuzzy chance for the original word to fall out again too.
			# otherwise it tends to be pretty unreadable.
			return transform_output_word(random.choice(wordcache[word] + [word] + [word]), punct)

def remove_punctuation(word):
	punctuations = ['.', ',', ';', ':', '-']
	# todo: braces?
	if any(word.endswith(p) for p in punctuations):
		punct = next(p for p in punctuations if word.endswith(p)) # don't do this op twice
		return (word[:-1], punct)
	return (word, None)

def transform_output_word(root_word, old_trailing_punct):
	# TODO: do this with lambdas
	return root_word + (old_trailing_punct if old_trailing_punct is not None else '')

def confuse_tokens(corpus_tokens):
	out = []
	for token in corpus_tokens:
		alt = fetch_word_alternative(token)
		if alt is not None:
			out.append(match_casing_of_existing_word(token, alt)) # use the synonym
		else:
			out.append(token) # no synonym for this word existed, so whatever
	return out

def match_casing_of_existing_word(old_word, new_word):
	# this is probably more work than it's worth.. i guess look at the word and figure out if it's:
	#	1. capitalized at the front (Title case)
	#	2. all caps (SHOUTING CASE)
	#	3. never capitalized (the way i like to see things)
	#	4. mixed case (sTatiSTicalAnomalies) - it's not the 80s, nobody writes like this anymore.
	if old_word.istitle():
		return new_word.title()
	elif old_word.isupper():
		return new_word.upper()
	else:
		return new_word.lower() # why not

def main():
	global API_KEY
	global BAD_RESULTS
	global DO_NOT_TRANSLATE

	if len(sys.argv) < 2:
		print 'Usage: %s {corpus}' % sys.argv[0]
		sys.exit(1)
	fp = open(sys.argv[1], 'r')

	corpus = fp.read()

	fp.close() # TODO: make better

	# CONFIG/AUTH
	cfg_stream = open('config.yml', 'r')
	config = yaml.safe_load(cfg_stream)
	API_KEY = config['api_key']
	DO_NOT_TRANSLATE = config['perfectly_good_words']
	BAD_RESULTS = config['bad_results']
	cfg_stream.close()

	# just load the word cache since we'll need it
	if os.path.exists('cache.dat'):
		prepopulate_runtime_cache('cache.dat')

	sentence = corpus.split()
	confused_sentence = confuse_tokens(sentence)
	print 'Original'
	print " ".join(sentence) + '\n'
	print 'Twisted!'
	print " ".join(confused_sentence) + '\n'

	# we're done here, so write the cache back out
	write_runtime_cache('cache.dat')

if __name__ == '__main__': main()
