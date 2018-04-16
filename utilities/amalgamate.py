import glob, os
import sys

os.chdir("subreddits")

lexiconList = []

# Read in the tsv files to lexiconList
for filename in glob.glob("*.tsv"):
    print("Reading in " + filename)

    file = open(filename, "r")
    for line in file:
        lexiconItem = line.split()
        strippedFileName = filename.replace(".tsv", "")  # We don't want the file extension
        lexiconItem.append(strippedFileName)
        lexiconList.append(lexiconItem)

# Sort lexiconList by first entry, the word itself
print("\nSorting Lexicon List")
lexiconList.sort(key=lambda x: x[0])

# Return to parent directory
os.chdir("..")

# Write lexiconList to lexicon.tsv
print("\nWriting to file")
output = open("lexicon.tsv","w")
for item in lexiconList:
    tsvEntry = "	".join(item)
    output.write(tsvEntry + "\n")
output.close()