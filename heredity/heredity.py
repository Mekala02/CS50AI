import csv
import itertools
import sys

# For fast debuging
# import os
# if len(sys.argv) != 2:
#     os.system("python heredity.py data/family2.csv")
#     sys.exit()


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
    # Probability of this specific world
    probability = 1
    # Looping over all people
    for person in people:
        # Determining person's gene for this possiblity
        gene = 1 if person in one_gene else 2 if person in two_genes else 0
        # Determining person's trait for this possiblity
        trait = True if person in have_trait else False
        # Determining person's mother, father
        mother = people[person]["mother"]
        father = people[person]["father"]
        # If we dont have mother, father information we using PROBS gene table for determining probability
        if mother == None:
            probability *= PROBS['gene'][gene]
        else:
            percentages = {}
            for mf in [mother, father]:
                # Determining mother and father's genes
                number = 1 if mf in one_gene else 2 if mf in two_genes else 0
                # Calculating passing probabilities acording to their genes(Including mutation probability)
                pass_per = 0 + PROBS['mutation'] if number == 0 else 0.5 if number == 1 else 1 - PROBS['mutation']
                percentages[mf] = pass_per
            if gene == 0:
                # Mom and Dad not transfered
                probability *= (1 - percentages[mother]) * (1 - percentages[father])
            elif gene == 1:
                # Mom not transfered, Dad trasnfered or Mom transfered, Dad not transfered
                probability *= (1 - percentages[mother]) * percentages[father] + percentages[mother] * (1 - percentages[father])
            else:
                # Mom and Dad transfared
                probability *= percentages[mother] * percentages[father]
        # Calculating trait probability for given values
        probability *= PROBS["trait"][gene][trait]
    return probability


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        gene = 1 if person in one_gene else 2 if person in two_genes else 0
        probabilities[person]["gene"][gene] += p
        probabilities[person]["trait"][person in have_trait] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    (We must normalize becouse we skipped some worlds in main function).
    """
    for person in probabilities:
        genemultiplayer = 1/sum(probabilities[person]["gene"].values())
        traitmultiplayer = 1/sum(probabilities[person]["trait"].values())
        for i in range(3):
            probabilities[person]["gene"][i] *= genemultiplayer
        for tf in [True, False]:
            probabilities[person]["trait"][tf] *= traitmultiplayer


if __name__ == "__main__":
    main()
