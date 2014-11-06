import wellactually as wa

assert len(wa.wordcache) == 0, "Word cache should be empty at startup"

# basic add
wa.add_synonyms_to_cache('emit', ['eject', 'discharge'])
assert len(wa.wordcache) == 3, "Three words should be produced when exposing three new words"
assert len(wa.wordcache['emit']) == 2, "Two synonyms for 'emit' should have been recorded"

wa.write_runtime_cache('test_cache.dat')

print 'pass'
