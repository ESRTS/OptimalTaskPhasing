from Time import *
from Task import Task

def main():

    task1 = Task('Task1', useconds(100), mseconds(100), mseconds(100), 0)

    print(task1)

    print(task1.utilization())

if __name__ == "__main__":
    main()