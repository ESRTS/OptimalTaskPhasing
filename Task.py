from Time import *
from drs import drs
import random
import math

class Task:
    """ Class to represent a periodic task """

    def __init__(self, task_name, task_wcet, task_period, task_deadline, task_offset, task_priority = 0):
        self.name = task_name           # Task name
        self.wcet = task_wcet           # Worst-Case Execution Time of the task
        self.period = task_period       # Period of the task
        self.deadline = task_deadline   # Deadline of the task
        self.offset = task_offset       # Offset of the task
        self.priority = task_priority   # Priority of the task
        self.responseTime = 0           # Response time of the task

    def utilization(self):
        """ Returns the task utilization """
        return self.wcet / self.period
    
    def __str__(self):
        """ Print task information. """
        return "Task: %s, T=%s, C=%s, D=%s, O=%s, P=%s, RT=%s" % (self.name, printTime(self.period), printTime(self.wcet), printTime(self.deadline), printTime(self.offset), self.priority, self.responseTime)
    
    def getJobsUntil(self, until):
        """ Returns a list of jobs that are released between 0 and until. """
        count = math.ceil(until / self.period)

        jobs = []

        for j in range(0,count,1):
            tmpJob = Job(self, j)
            jobs.append(tmpJob)

        return jobs

class Job:
    """ Class to represent a job/instance of a task. """
    def __init__(self, job_task, job_id):
        self.task = job_task                                            # Task the job belongs to
        self.id = job_id                                                # ID of the job, starting with 0
        self.release = (self.id * self.task.period) + self.task.offset  # Release time of the job
        self.deadline = self.release + self.task.deadline               # Deadline of the job

    def __str__(self):
        """ Print job information. """
        return "Job(%s, %s): r = %s, d = %s" % (self.task.name, self.id, printTime(self.release), printTime(self.deadline))

def generateRandomTasks(count, utilization):
    """ Function to generate a set of random tasks """
    tasks = []
    periods = [1, 2, 5, 10, 20, 50, 100, 200, 1000] # Periods from "Real world automotive benchmark for free" WATERS 2015
    utilizations = drs(count, utilization)
    id = 0

    for u in utilizations:
        period = mseconds(random.choice(periods))
        wcet = math.ceil((u * period) / 1)
        
        tasks.append(Task("Task_%s" % (id), wcet, period, period, 0))
        id += 1

    frac, i = math.modf(tasksetUtilization(tasks) * 100)
    assert (i == utilization * 100)   # Make sure the utilization is correct on two decimals

    return tasks

def tasksetUtilization(tasks):
    """ Function to compute the utilization of a taskset. """
    utilization = 0.0

    for t in tasks:
        utilization += t.utilization()

    return utilization

def isMaxHarmonic(tasks):
    """ Function returns true of the task set is max harmonic. I.e. the largest task period can be evenly divided by all other periods. """

    # Get the largest period in the task set
    maxPeriod = getMaxPeriod(tasks)

    # Check if all periods evenly divide the largest task period
    for t in tasks:
        if maxPeriod % t.period != 0:
            return False

    return True

def getMaxPeriod(tasks):
    """ Function returns the largest task period. """
    maxPeriod = 0
    for t in tasks:
        if t.period > maxPeriod:
            maxPeriod = t.period
    
    return maxPeriod

def getMax2Period(tasks):
    """ Function returns the second largest period (or 0). """
    max1Period = 0
    max2Period = 0

    for t in tasks:
        if t.period > max1Period:
            max2Period = max1Period
            max1Period = t.period
        elif t.period < max1Period:
            if t.period > max2Period:
                max2Period = t.period
    
    return max2Period

def hyperperiod(tasks):
    """ Returns the hyperperiod of the taskset """
    periods = []

    for t in tasks:
        if not t.period in periods:
            periods.append(t.period)
    
    return math.lcm(*periods)

def chainString(chain):
    retval = str(chain[0].period)

    for task in chain[1:]:
        retval = retval + ' -> ' + str(task.period)

    return retval

if __name__ == '__main__':
    """ Debugging """
    random.seed(123)

    task1 = Task('Task1', useconds(100), mseconds(100), mseconds(100), 0)

    print(task1)

    print(task1.utilization())

    job = Job(task1, 0)

    jobs = task1.getJobsUntil(mseconds(500))

    for j in jobs:
        print(j)

    tasks = generateRandomTasks(10, 1)

    for t in tasks:
        print(t)

    print("Utilization: " , tasksetUtilization(tasks))

    print("Max. Harmonic: " , isMaxHarmonic(tasks))