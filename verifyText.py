#!/usr/bin/env python
import json, sys, re

WINDOW_WIDTH = 48
WINDOW_HEIGHT = 5

RE_SPLIT_WORDS = re.compile("[^a-zA-Z0-9]+")

### START SPELL CHECKING ###
# http://norvig.com/spell-correct.html

OFFICIAL_NAMES = """
Albo
Algath
Blackbeard
Bob
Bullghur
Chompa
Cucumbro
Edward
Ema
Fiffilina
Filou
Finata
Foxan
Froggo
Frostvale
Goatie
Gomgom
Gorky
Gosie
Goulda
Grodo
Gulhrug
Ilgith
Karkarh
Kuuyi
Landlubber
Lockwoods
Lubo
Luna
Maduna
Minai
Morwyn
Nimbul
Oakstone
Ollghar
Oozemaw
Osamon
Pala
Pila
Shroom
Shrooms
Sorkorh
Urkarh
Xin
Zean
"""

import re, collections

verified_words = {}

def words(text): return re.findall('[a-z]+', text.lower())

def train(features):
    model = collections.defaultdict(lambda: 1)
    for f in features:
        model[f] += 1
    return model

NWORDS = train(words(OFFICIAL_NAMES))

alphabet = 'abcdefghijklmnopqrstuvwxyz'

def edits1(word):
   splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
   deletes    = [a + b[1:] for a, b in splits if b]
   transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
   replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
   inserts    = [a + c + b     for a, b in splits for c in alphabet]
   return set(deletes + transposes + replaces + inserts)

def known_edits2(word):
    return set(e2 for e1 in edits1(word) for e2 in edits1(e1) if e2 in NWORDS)

def known(words): return set(w for w in words if w in NWORDS)

def correct(word):
    candidates = known([word]) or known(edits1(word)) or known_edits2(word) or [word]
    return max(candidates, key=NWORDS.get)
### END SPELL CHECKING ###

def simRender(msg):
  ret = 1
  pos = WINDOW_WIDTH
  while pos<len(msg):
    ret += 1
    pos0 = msg.rfind(' ', 0, pos)
    if pos==-1:
      raise Exception('No space in string: "%s"' % msg)
    pos += WINDOW_WIDTH
  return ret

def verifyMsg(path, msg):
  if "-w" in OPTIONS:
    for page in msg.split("/"):
      num_lines = simRender(page)
      if num_lines>WINDOW_HEIGHT:
        print '\nLines too long in %s: "%s"' % (path,page)
        break

  if "-s" in OPTIONS:
    for word in RE_SPLIT_WORDS.split(msg):
      w = word.lower()
      if word and word[0].isupper() and not verified_words.has_key(w):
        corrected = correct(w)
        verified_words[w] = True
        if corrected!=w and corrected[0]==w[0]:
          print '\nPotential typo in %s: "%s" should be "%s"?' % (path, word, corrected.capitalize())

def processDict(path, v):
  t = type(v)
  if t==dict:
    for k0, v0 in v.iteritems():
      if k0!='description':
        processDict(path+"->"+k0, v0)
  elif t==unicode:
    verifyMsg(path, v)
  else:
    raise Exception("Error while processing type", t)

OPTIONS = sys.argv[2:]
if not OPTIONS:
  print "Usage:", sys.argv[0], "file.txt <options>"
  print "    -w: verify text for dialog windows width and height"
  print "    -s: verify spelling for potential name typos"
  sys.exit(0)

f=open(sys.argv[1], "r")
a=f.read()
f.close()

try:
  t=json.loads(a)
except Exception as ex:
  print "ERROR:", ex

processDict("", t)

print "\n-- Verification complete"

