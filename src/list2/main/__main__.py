import math
from string import punctuation
from itertools import groupby
from collections import Counter

PATH_BOOK = "C:\\myTrash\\PWr\\9semestr\\ED\\LabDM_236616\\src\\list2\\txt\\book_en.txt"
PATH_CHAP = "C:\\myTrash\\PWr\\9semestr\\ED\\LabDM_236616\\src\\list2\\txt\\chapters\\chapter_"
PATH_CHAP_IDX = "C:\\myTrash\\PWr\\9semestr\\ED\\LabDM_236616\\src\\list2\\txt\\chapters\\chapter_tf_"
PATH_STOPWORDS = "C:\\myTrash\\PWr\\9semestr\\ED\\LabDM_236616\\src\\list2\\txt\\stopWords_en.txt"
PATH_OUT = "C:\\myTrash\\PWr\\9semestr\\ED\\LabDM_236616\\src\\list2\\txt\\list_en.csv"
PATH_RND = "C:\\myTrash\\PWr\\9semestr\\ED\\LabDM_236616\\src\\list2\\txt\\random_chapter.txt"
CHAP_SEPARATOR = "Chapter"
MULTI = 100_000
NUM_MATCHING_CHAPTERS = 5
NUM_NEIGHBOURS = 5


def generate_word_cloud(path_in, stopwords_path_in):
    words = read_words(path_in)
    stopwords = read_words(stopwords_path_in)  # , enc="utf-8")
    stopwords.append("")

    words_lower_case = [word.lower().translate(str.maketrans('', '', punctuation))
                        for word in words]
    filtered_words = [word for word in words_lower_case if word not in stopwords]

    pairs = [(w, 1) for w in filtered_words]
    pairs.sort()

    mapper = lambda pair: pair[0]
    grouped_pairs = [(w, sum(1 for _ in g)) for w, g in groupby(pairs, key=mapper)]

    occurrences = lambda pair: pair[1]
    grouped_pairs.sort(key=occurrences, reverse=True)
    return grouped_pairs


def save_word_cloud(list_words, path_out):
    with open(path_out, encoding="UTF-8", mode="w") as f:
        for pair in list_words:
            line: str = str(pair[1]) + "," + str(pair[0]) + "\n"
            f.write(line)


def divide_into_chapters(path_in, path_out, chapter_separator):
    chapter_number = 1
    output_file = open(get_chapter_name(path_out, chapter_number), 'w')

    with open(path_in, encoding="UTF-8") as f:
        for line in f:
            if chapter_separator in line:
                output_file.close()
                chapter_number += 1
                output_file = open(get_chapter_name(path_out, chapter_number), mode='w')
            output_file.write(line)
    return chapter_number


def get_chapter_name(base, number, ext="txt"):
    return base + str(number) + "." + ext


def find_matching_chapters(list_of_maps):
    while True:
        entered = input("Please, type a word. I will find most matching chapters of specified word.\n")
        # best = [0] * len(list_of_maps)
        best = {}
        i = 0
        for m in list_of_maps:
            if m.__contains__(entered):
                best[i + 1] = m[entered]
            i += 1

        best = sorted(best.items(), key=lambda x: x[1], reverse=True)
        i = 0
        while i < NUM_MATCHING_CHAPTERS:
            if i < best.__len__():
                print(str(best[i][0]) + ": " + str(best[i][1]))
            i += 1


def find_indexes():
    list_of_chapters = []
    # n = divide_into_chapters(PATH_BOOK, PATH_CHAP, CHAP_SEPARATOR)
    n = 40
    num_words = []
    list_of_maps = []
    single_occurrs = []
    i = 1

    while i < n:
        seq = generate_word_cloud(get_chapter_name(PATH_CHAP, i), PATH_STOPWORDS)
        copied = {}
        zeros = {}
        num_words.append(0)
        # num_words.__add__([0])
        list_of_chapters.append(seq)

        for pair in seq:
            num_words[i - 1] = num_words[i - 1] + pair[1]
            copied[pair[0]] = pair[1]
            zeros[pair[0]] = 0
        list_of_maps.append(copied)
        single_occurrs.append(zeros)
        i += 1

    print("OK")
    for arr in list_of_chapters:
        for pair in arr:
            i = 0
            while i < n - 1:
                if single_occurrs[i].__contains__(pair[0]):
                    single_occurrs[i][pair[0]] += 1
                i += 1

    i = 0
    print("OK")
    for arr in list_of_chapters:
        for pair in arr:
            n_ij = pair[1]
            s = num_words[i]
            sum_d = single_occurrs[i][pair[0]]

            list_of_maps[i][pair[0]] = int(MULTI * n_ij / s * math.log(n / sum_d))
        i += 1

    i = 1
    for arr in list_of_maps:
        # to_list = list(arr)
        # to_list.sort()
        arr = sorted(arr.items(), key=lambda x: x[1], reverse=True)
        save_word_cloud(arr, get_chapter_name(PATH_CHAP_IDX, i, ext="csv"))
        i += 1

    return list_of_maps


def read_words(path, enc=None):
    with open(path, encoding=enc) as f:
        word_list = [word
                     for line in f
                     for word in line.split()]
    return word_list


def generate_random_paragraph(path_in, stopwords_path_in, rnd_path_out):
    words = read_words(path_in)
    stopwords = read_words(stopwords_path_in)  # , "UTF-8")
    stopwords.append("")

    # filter of stop words, standard procedure:
    words_lower_case = [word.lower().translate(str.maketrans('', '', punctuation))
                        for word in words]
    filtered_words = [word for word in words_lower_case if word not in stopwords]

    lists = [(w, []) for w in filtered_words]

    # add 5 neighbours to list:
    for i in range(0, lists.__len__()):  # word_list in filtered_words:
        j = 1
        while j <= NUM_NEIGHBOURS and i + j < lists.__len__():
            lists[i][1].append(lists[i + j][0])
            j += 1

    word_lambda = lambda pair: pair[0]
    lists.sort(key=word_lambda)

    # add repetiting words to first pair
    i = 0
    list_of_i = []
    size = lists.__len__()
    while i < size:
        word = lists[i][0]
        j = 1
        while i + j < size and lists[i + j][0] == word:
            # lists[i][1].append(lists[i + j][1])

            for w in lists[i + j][1]:
                lists[i][1].append(w)
            # lists[i][1] = lists[i][1].__add__(lists[i + j][1])
            j += 1
        list_of_i.append(i)
        i = i + j

    # reduce lists to unique: word -> all it's neighbours up to 5 per word
    new_lists = []
    i = 0
    while i < size:
        if list_of_i.__contains__(i):
            new_lists.append(lists[i])
        i += 1

    # add new list with empty list
    grouped_list = []
    for word_list in new_lists:
        grouped_list.append((word_list[0], []))

    # group words and count their neighbours
    i = 0
    for word_list in new_lists:
        neighbours = lambda v: v[0]
        counted = lambda v: v[1]
        # values = [(w, 1) for w in word_list[1]]
        # grouped_pairs = [(w, sum(1 for _ in g)) for w, g in groupby(lists, key=mapper)]
        # grouped = [(w, sum(1 for _ in g)) for w, g in groupby(values, key=neighbours)]
        grouped = Counter(word_list[1])

        for w in grouped:
            grouped_list[i][1].append((w, grouped[w]))
        grouped_list[i][1].sort(key=counted, reverse=True)
        i += 1

    new_chapter = []

    for word_neigh in grouped_list:
        new_chapter.append(word_neigh[0])
        i = 0
        while i < NUM_NEIGHBOURS and i < len(word_neigh[1]):
            new_chapter.append(word_neigh[1][i][0])
            i += 1

    with open(rnd_path_out, encoding="UTF-8", mode="w") as f:
        i = 0
        breakline = 20
        for w in new_chapter:
            f.write(str(w) + " ")
            if i == breakline:
                f.write("\n")
                i = 0
            i += 1

    print("a")
    # neighbours = lambda word_list: word_list[1]
    # grouped_neighbours = [(w, sum(a for a in g)) for w, g in groupby(lists, key=neighbours)]
    # # grouped_pairs = [(w, sum(1 for _ in g)) for w, g in groupby(lists, key=neighbours)]
    #
    # value = lambda v: v
    #
    # for word_list in grouped_neighbours:
    #     grouped = [(w, sum(1 for _ in g)) for w, g in groupby(word_list[1], key=value)]
    #     word_list[1].sort()
    # occurrences = lambda word_list: word_list[0]
    # grouped_neighbours.sort(key=occurrences, reverse=True)
    # return grouped_neighbours


def main():
    print("hello world")
    # words = get_word_cloud(PATH_BOOK, PATH_STOPWORDS)
    # save_word_cloud(words, PATH_OUT)
    # divide_into_chapters(PATH_BOOK, PATH_CHAP, CHAP_SEPARATOR)

    list_of_maps = find_indexes()
    find_matching_chapters(list_of_maps)

    generate_random_paragraph(PATH_BOOK, PATH_STOPWORDS, PATH_RND)

    print("hello")


if __name__ == '__main__':
    main()
