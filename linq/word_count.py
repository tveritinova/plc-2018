from linq import linq

print (linq(open("words", "r").readlines())
    .Select(lambda line: line.split())
    .Flatten()
    .GroupBy(lambda word: word)
    .Select(lambda item: (item[0], len(item[1])))
    .OrderBy(lambda item: item[1])
    .Select(lambda item: item[0]+": "+str(item[1]))
    .ToList())