# ToDo

## Corrupte dataset

Sommige regels bevatten meer dan 5 columns?

```
> cat 2id26_dataset_orig.csv | awk -F',' '{ print NF; }' | sort | uniq -c | sort
    111 2
    115 4
     14 8
   1540 5
    183 6
      2 10
     30 7
     31 0
      3 9
     71 1
      8 3
```
