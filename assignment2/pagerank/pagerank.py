import os
import random
import re
import sys
from copy import copy

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
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


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    linkChances = {}
    # get probabilities for each page
    for webPage in corpus:

        # if linked to that page from current page
        if webPage in corpus[page]:

            """chance to go to that page would be chance go link instead random
            divided by each link you can access
            plus chance it picks any random page"""
            linkChances[webPage] = damping_factor / len(corpus[page]) \
                + (1 - damping_factor) / len(corpus)

        else:  # else its just the chance of picking random page
            linkChances[webPage] = (1 - damping_factor) / len(corpus)

    # return
    return linkChances


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # init chances/popularity for each page
    overallChances = {}
    for webPage in corpus:
        overallChances[webPage] = 0

    # pick a random page to start
    page = list(corpus.keys())[random.randint(0, len(corpus) - 1)]

    # add to the chances of getting that page
    overallChances[page] += 1 / n

    # chances of the next pages we can go to
    chances = transition_model(corpus, page, damping_factor)

    # sampling, doesn't include first round (already done above)
    for i in range(1, n):

        # get what next page is (based off the chances from last page)
        page = random.choices(list(chances.keys()), list(chances.values()))[0]

        # increment chances of getting that page
        overallChances[page] += 1 / n

        # getting chances of next page you can go on based on new page
        chances = transition_model(corpus, page, damping_factor)

    return overallChances


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # first assume chances to get to each webpage is equal
    overallChances = {}
    for webPage in corpus:
        overallChances[webPage] = 1 / len(corpus)

    """ then, for each webpage, find how likely each webpage is
    depending on amount of links from other pages"""
    while True:
        # copy of what chances were before next iteration below
        originalChances = copy(overallChances)

        # update each webpages chances
        for webPage in corpus:

            # chances someone came from other page
            fromOtherPage = 0

            # each page
            for page in corpus.keys():
                # if that page connects to current page
                if webPage in corpus[page]:
                    # find amount of links connecting to that to base its worth
                    if len(corpus[page]):
                        fromOtherPage += originalChances[page] / len(corpus[page])
                    else:  # if no links then interpreted as links to all pages
                        fromOtherPage += originalChances[page] / len(corpus)

            # combine with chances surfer clicked on random page
            overallChances[webPage] = (1 - damping_factor) / len(corpus) + \
                damping_factor * fromOtherPage

        # if no significant change in chances then return
        for key in overallChances.keys():
            # changes in chance still happening = keep iterating
            if "%.4f" % originalChances[key] != "%.4f" % overallChances[key]:
                break
        else:  # no more changes then return
            return overallChances


if __name__ == "__main__":
    main()
