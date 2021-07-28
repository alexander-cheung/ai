import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    allNames = set(people.keys())

    # chances of all things specified happening together
    jointProb = 1

    """ since multiply can go any order, we can split probs into 2 parts
    ie person 1 gene and no trait into calc gene, trait in separate parts"""

    # calculating for zero gene people
    for person in allNames - one_gene - two_genes:
        # prob they have no bad gene
        jointProb *= probGene(people, one_gene, two_genes, have_trait, person, 0)
        # prob they have/dont have trait
        jointProb *= probTrait(person, have_trait, 0)
    for person in one_gene:
        # prob 1 bad gene
        jointProb *= probGene(people, one_gene, two_genes, have_trait, person, 1)
        # prob have/no have trait
        jointProb *= probTrait(person, have_trait, 1)
    for person in two_genes:
        # prob 2 bad gene
        jointProb *= probGene(people, one_gene, two_genes, have_trait, person, 2)
        # prob have/no have trait
        jointProb *= probTrait(person, have_trait, 2)

    return jointProb

def probGene(people, one_gene, two_genes, have_trait, person, geneAmount):
    """returns the probability someone has x amounts of gene"""
    mother = people[person]["mother"]
    momGene = 0
    father = people[person]["father"]
    dadGene = 0
    # probability they have x amounts genes
    geneProb = 1

    if mother and father:
        # chance mom passes gene on
        if mother in one_gene:
            # chance you get bad gene or reg gene and mutates 
            momGene = 0.50 + PROBS["mutation"]
        elif mother in two_genes:
            # you get bad gene but might mutate to normal        
            momGene = 1 - PROBS["mutation"]
        else:  # no bad gene but might mutate
            momGene = PROBS["mutation"]

        # chance dad passes gene on
        if father in one_gene:
            # chance you get bad gene or reg gene and mutates 
            dadGene = 0.50 + PROBS["mutation"]
        elif father in two_genes:
            # you get bad gene but might mutate to normal
            dadGene = 1 - PROBS["mutation"]
        else:  # no bad gene but might mutate
            dadGene = PROBS["mutation"]

    if geneAmount == 0:
        if mother and father:
            # the chance that they both don't have the gene
            geneProb = (1 - momGene) * (1 - dadGene)
        else:  # no mom or dad given, just use unconditional values
            geneProb = PROBS["gene"][0]
    elif geneAmount == 1:
        if mother and father:
            # chance one passes it down
            geneProb = (1 - momGene) * dadGene + momGene * (1 - dadGene)
        else:  # no mom or dad given, just use unconditional values
            geneProb = PROBS["gene"][1]
    elif geneAmount == 2:
        if mother and father:
            # chance they both have it
            geneProb = momGene * dadGene
        else:  # no mom or dad given, just use unconditional values
            geneProb = PROBS["gene"][2]

    return geneProb

def probTrait(person, have_trait, geneAmount):
    """returns either the probability they have the trait or don't depending on gene"""
    if person in have_trait:
        return PROBS["trait"][geneAmount][True]
    else:
        return PROBS["trait"][geneAmount][False]


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    # iterate over each person's dict
    for person, pDist in probabilities.items():
        # update correct gene chance
        if person in one_gene:
            pDist["gene"][1] += p
        elif person in two_genes:
            pDist["gene"][2] += p
        else:
            pDist["gene"][0] += p
        # update correct trait chance
        if person in have_trait:
            pDist["trait"][True] += p
        else:
            pDist["trait"][False] += p

def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    # iterate over each person's dict
    for person in probabilities.values():

        # each probability dist in person dict
        for name, pDist in person.items():
            # current total of all probs
            total = sum(list(pDist.values()))

            # total can't be 0
            if not total:
                raise Exception("probability is 0")

            # normalizing factor
            nFactor = 1 / total

            # update each probability by the normalizing factor
            person[name] = {key: percent * nFactor for key, percent in pDist.items()}

if __name__ == "__main__":
    main()
