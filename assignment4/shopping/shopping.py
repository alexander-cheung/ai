import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4

# easier than importing a module
month_to_number = {
    'jan': 0,
    'feb': 1,
    'mar': 2,
    'apr': 3,
    'may': 4,
    'june': 5,
    'jul': 6,
    'aug': 7,
    'sep': 8,
    'oct': 9,
    'nov': 10,
    'dec': 11}

def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    evidence = []
    labels = []

    # using these functions in order to convert data (none is special func)
    types = [int, float, int, float, int, float, float, float,
             float, float, None, int, int, int, int, None, None]

    with open(filename, newline="") as data:
        reader = csv.reader(data)

        # skip over headers
        next(reader)

        # add to evidence and labels for each line in file
        for line in reader:
            # all evidence for line
            pieceEvidence = line

            # get label in evidence and append
            label = 1 if pieceEvidence.pop() == "TRUE" else 0
            labels.append(label)

            # convert each piece to right type
            for i in range(len(pieceEvidence)):
                if types[i]:
                    pieceEvidence[i] = types[i](pieceEvidence[i])
                # special cases must hardcode in
                elif i == 10:  # month to num
                    pieceEvidence[i] = month_to_number[pieceEvidence[i].lower()]
                elif i == 15:  # visitor type to int
                    pieceEvidence[i] = 1 if pieceEvidence[i] == "TRUE" else 0
                elif i == 16:  # weekend to int
                    pieceEvidence[i] = 1 if pieceEvidence[i] == "TRUE" else 0
            # append evidence
            evidence.append(pieceEvidence)
    # return as tuple
    return evidence, labels


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    classifier = KNeighborsClassifier(n_neighbors=1)
    classifier.fit(evidence, labels)

    return classifier


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificty).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    correctPositive = 0
    totalPositive = 0
    correctNegative = 0
    totalNegative = 0

    # each label and prediction
    for label, prediction in zip(labels, predictions):
        # increment right predictions and total neg
        if label == 0:
            totalNegative += 1
            if label == prediction:
                correctNegative += 1

        # increment right predictions and total positive
        elif label == 1:
            totalPositive += 1
            if label == prediction:
                correctPositive += 1

    # rate of right positive and negative
    sensitivity = correctPositive / totalPositive
    specificity = correctNegative / totalNegative

    return sensitivity, specificity


if __name__ == "__main__":
    main()
