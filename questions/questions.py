import nltk
import os
import string
import math
import sys

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


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
    files_contents = {}
    for text in os.listdir(directory):
        with open(os.path.join(directory, text), encoding="utf-8") as f:
            files_contents[text] = f.read()
    return files_contents


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    processed = []
    for word in nltk.word_tokenize(document.lower()):
        if word not in nltk.corpus.stopwords.words("english") and word not in string.punctuation:
            processed.append(word)
    return processed


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    words = set()
    idfs = dict()

    for f in documents:
        words.update(set(documents[f]))
    for word in words:
        # ndc: Number of documents containing that word
        ndc = sum(word in documents[filename] for filename in documents)
        idf = math.log(len(documents) / ndc)
        idfs[word] = idf
    return idfs


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    tfidfs = {}
    for f in files:
        tfidf = 0
        for word in query:
            tfidf += idfs[word] * files[f].count(word)
        tfidfs[f] = tfidf

    sorted_tfidfs = sorted(tfidfs.items(), key=lambda x: x[1], reverse=True)
    return [x[0] for x in sorted_tfidfs[:n]]


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    result = {}
    for sentence in sentences:
        idf = 0
        total_words = 0
        for word in query:
            if word in sentences[sentence]:
                total_words += 1
                idf += idfs[word]
        result[sentence] = (idf, float(total_words) / len(sentences[sentence]))
    sorted_results = sorted(result.items(), key=lambda x: (x[1][0], x[1][1]), reverse=True)
    return [x[0] for x in sorted_results[:n]]


if __name__ == "__main__":
    main()
