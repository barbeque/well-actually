import wellactually as wa

assert len(wa.wordcache) == 0, "Word cache should be empty at startup"

# basic add
wa.add_synonyms_to_cache('emit', ['eject', 'discharge'])
assert len(wa.wordcache) == 3, "Three words should be produced when exposing three new words"
assert len(wa.wordcache['emit']) == 2, "Two synonyms for 'emit' should have been recorded"

# test save and load
wa.write_runtime_cache('test_cache.dat')
wa.add_synonyms_to_cache('bad', ['michael jackson', 'thriller'])
assert 'michael jackson' in wa.wordcache.keys(), "Didn't save a synonym as a primary key, which defeats bidirectionality."
wa.prepopulate_runtime_cache('test_cache.dat')
assert len(wa.wordcache) == 3, "Three words should have been reloaded from file, not %d" % len(wa.wordcache)
assert not 'michael jackson' in wa.wordcache.keys(), "Old key was not erased when we reloaded a saved dictionary cache."

print 'pass'
