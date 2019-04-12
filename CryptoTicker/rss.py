import feedparser

d = feedparser.parse('http://pplware.sapo.pt/feed/')

print d['feed']['title']
for post in d.entries:
    print post.title
