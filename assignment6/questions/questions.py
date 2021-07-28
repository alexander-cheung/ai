import nltk
import sys
import os
from string import punctuation
from numpy import log

FILE_MATCHES = 1
SENTENCE_MATCHES = 1

FILTER = nltk.corpus.stopwords.words("english") + list(punctuation)

def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    fileTexts = {}
    # every file in directory
    _, _, filenames = next(os.walk(directory))

    # each file
    for fileName in filenames:
        with open(os.path.join(directory, fileName), "r") as file:
            fileTexts[fileName] = file.read()

    return fileTexts


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    words = filter(lambda token : token not in FILTER, nltk.tokenize.word_tokenize(document))
    words = [word.lower() for word in words]
    return words


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    numDocs = len(documents)
    wordIDFs = {}

    # all documents in lowercase only
    docsSmall = []
    for article in documents.values():
        docsSmall.append([word.lower() for word in article])

    # each set words
    for words in docsSmall:

        # each word
        for word in set(words):

            word = word.lower()

            # word not yet has idf
            if not wordIDFs.get(word):

                # find number of docs with that word in it
                docsWithWord = 0

                for article in docsSmall:
                    if word in article:
                        docsWithWord += 1

                # calculate idf
                wordIDFs[word] = log(numDocs / docsWithWord)

    return wordIDFs


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    rankings = {}

    for docName, article in files.items():

        rankings[docName] = 0
        for word in query:
            # get doc idf
            idf = idfs.get(word, 0)

            tf = 0
            # only if term exists
            if idf:
                # find document tf
                for term in article:
                    if word == term:
                        tf += 1

            rankings[docName] += idf * tf

    return sorted(rankings, key=lambda doc: rankings[doc], reverse=True)[:n]


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    sentRank = {}

    # each sent in doc
    for key, sentence in sentences.items():
        # find amount of query words in sent
        rank = 0
        qTermDensity = 0

        for word in query:
            appeared = sentence.count(word.lower())
            # add idf for each word found
            if appeared:

                rank += idfs.get(word)

                # also keep track of how much query terms appear in sent
                qTermDensity += appeared / len(sentence)

        sentRank[key] = (rank, qTermDensity)

    return sorted(sentRank, key=lambda sent: sentRank[sent], reverse=True)[:n]


if __name__ == "__main__":
    main()
