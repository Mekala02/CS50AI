import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000

# For fast debuging
# if len(sys.argv) != 2:
#     os.system("python pagerank.py corpus2")
#     sys.exit()


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    print(corpus)
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


'''
Choosing site according to transition models pages likelihoods
'''


def weighted_random(transition_model):
    rndm = random.random()
    for pagename, probability in transition_model.items():
        rndm -= probability
        if rndm <= 0:
            return pagename


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    allpagescount = len(corpus)
    pagesprobs = dict()
    currentpageslinkcount = len(corpus[page])
    if currentpageslinkcount == 0:
        # If that page doesn't have any link: We will treat it like it has all pages links
        for pagename in corpus:
            pagesprobs[pagename] = 1/allpagescount
        return pagesprobs
    else:
        '''
        Iterating over all pages. If pages link is in the currentpages links then calculating its likelihood by
        damping_factor and number of links in the site.
        Else we calculating its likelihood using (1-damping_factor) multiplier
        '''
        for pagename in corpus:
            if pagename in corpus[page]:
                pagesprobs[pagename] = (damping_factor/currentpageslinkcount)
            else:
                pagesprobs[pagename] = (1-damping_factor)/(allpagescount-currentpageslinkcount)
    return pagesprobs


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Defining counter dict and adding pages to it for counting their popularities
    counter = dict()
    for name in corpus.keys():
        counter[name] = 0

    # Getting initial page randomly from all pages
    initialpage = random.choice(list(corpus.items()))
    currentpage = initialpage[0]

    # Generating n samples
    for i in range(n):
        # Adding 1 to number of visits to current page that we are in
        counter[currentpage] += 1
        # Selecting pages for visiting, by their likelihood
        currentpage = weighted_random(transition_model(corpus, currentpage, damping_factor))
    # Dividing all counters by n
    for name in counter.keys():
        counter[name] = (counter[name]/n)
    return counter


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    popularity = dict()
    # Initially setting all pages likelihood equal
    for name in corpus.keys():
        popularity[name] = 1/len(corpus)
    # Updates pages popularity until they stabilize
    while True:
        # For detecting changes on pages popularities
        previus = dict(popularity)
        # Selecting site for updating it's popularity
        for pname in corpus.keys():
            sum = 0
            # Iterating all pages
            for iname in corpus.keys():
                if pname in corpus[iname]:
                    sum += popularity[iname]/len(corpus[iname])
                # If page has no links, we can pretend like it has links to all pages that in the corpus, including itself
                if len(corpus[iname]) == 0:
                    sum += (popularity[iname]) / len(corpus)
            # Updating pages popularity
            popularity[pname] = ((1-damping_factor)/len(corpus))+(damping_factor*sum)
        # Substracting new popularities from old one for check differance
        differance = {key: popularity[key] - previus.get(key, 0) for key in popularity.keys()}
        # Checking if differance within the tolerance, if its ideal returning the popularity
        for value in differance.values():
            if abs(value) > 0.001:
                break
        else:
            return(popularity)


if __name__ == "__main__":
    main()
