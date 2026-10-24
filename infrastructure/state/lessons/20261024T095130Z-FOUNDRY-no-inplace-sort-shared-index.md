Never list.sort() a list you got out of a shared index inside a ThreadPoolExecutor: CPython empties the list for the duration of the sort, so another thread reads [] (fauna_spec texture index, fixed cb6c332768). Use sorted().
home: NONE
