![alt text](./images/yoyodyne_data_science_logo.png "Yoydyne Data Science")

# Distribution-free Tolerance Intervals

In this README and accompanying notebook I'll explain some functions I wrote for calculating distribution-free tolerance intervals. Almost all the equations in those functions are directly reproduced from the excellent book *'Statistical Intervals A Guide for Practitioners and Researchers'* by William Q. Meeker, Gerald J. Hahn, Luis A. Escobar (Wiley, 2017), predominantly Chapter 5 (*Distribution-Free Statistical Intervals*). Before going into detail on these equations and their applications, let's provide a clear example where distribution-free tolerance intervals are required.

## Example: Estimating the time taken to complete a task

For our example, let's consider the time taken to complete some task. We'll imagine there's one worker (or a series of workers with identical competencies at completing the task) who completes a number of these tasks in a given time. We have at our disposal then a sample of task completion times, and this sample is taken from an *a priori* unkown distribution of task completion times. Although the exact pdf for task completion times for this task is not known to us, we know that, in general it will look something like this:

<p align="center">
  <img width="600" src="images/task_completion_time_n_eq_5000.png">
</p>

The features I want to draw attention to in this plot are the following:

- The distribution has a clear peak (it's somewhere around 8 mins in this example). This tells us that the task has a typical completion time associated with it, and a large number of tasks are completed in a window containing this peak
- The distribution has a long tail. This tells us that, infrequently, tasks can take a lot longer to complete than expected. For example there might be some complication which means a particular task in our sample took longer to complete than it typically would.
- The distribution only covers the positive half of the time axis. That is, tasks take a finite amount of time to complete.

This third point may seem trivial, but many distributions, including the normal distribution have support from -&#8734; to +&#8734;, so we should always be wary when invoking them in such situations: the probability for completing a task in any time < 0 must equal 0. N.B. You'll notice in the notebook, that I generated this data by sampling from an Erlang distribution. I'll discuss this distribution a little later, but for now all that's important is that it generates data with the three properties listed above.

## Task completion statistic

Given the above data, we'd like to provide a statistic on the task completion time. Typically, given some sample, we'd calculate the mean and standard deviation and that would be that. Let's calculate these properties and overlay them on the plot above:

<p align="center">
  <img width="600" src="images/task_completion_time_n_eq_5000_withmean.png">
</p>

This image should sound some alarm bells about the validity of simply quoting &#956; ± &#963; (i.e. mean ± standard deviation). The mean is shifted to the right due to the long tail, leading to a value which isn't indicative of the time it typically takes to complete this task. Moreover, the symmetric nature of &#956; ± &#963; belies the fact that completion times are much more likely to occur in a window &#956;-&#963;<*t*<&#956; than in the period &#956;<*t*<&#956;+&#963;. Furthermore, if we require more certainty in our statistic by quoting 2&#963; bounds on the mean we get into huge trouble as &#956;-2&#963; stretches into the negative part of the time axis!

## Summary statistics for non-normal distributions

The previous section convinced us that quoting &#956; ± &#963; for a non-symmetric pdf with support for only positive values of the random value, was of little value. But why the obsession with this window of plus-minus one standard deviation around the mean? Let's refresh our knowledge of the normal distribution with the aid of the plot below: 

<p align="center">
  <img width="800" src="images/normal_distribution.png">
</p>

We see that (approximately) 68% of the probability density is contained within the interval &#956; ± &#963;. As we increase the interval (becoming more conservative in our estimate) we capture a greater density of probability, e.g. approximately 95% and 99.7% for &#956; ± 2&#963; and &#956; ± 3&#963;, respectively. This gives us an alternative interpretation for the standard &#956; ± &#963; statistic; it defines the (narrowest possible) interval which contains 68% of the population. Perhaps then, instead of focussing on means and standard deviations, we can ask the question *What is the (narrowest possible) interval containing n% of the population?*. Such a statistic makes no assumption about the symmetry or support of a pdf.

N.B. the slightly pedantic inclusion "narrowest possible" in the preceding paragraph. For a given probability distribution *P(x)*, there are an infinite number of choices of *x*<sub>*1*</sub> and *x*<sub>*2*</sub> s.t. &#8747;*P*(*x*<sub>*1*</sub><x<*x*<sub>*2*</sub>) (for example *x*<sub>*1*</sub> = 0, *x*<sub>*2*</sub> = `any_scipy_continuous_random_variable.ppf(0.68)`). The most pertinent choice is the one which minimizes *x*<sub>*2*</sub> &#8722; *x*<sub>*1*</sub>.

## Task completion statistic revisited

Ok so with this in mind, let's return to our task completion data. Now instead of calculating a mean and a standard deviation, we're going to look for an interval which contains 68% of the population. As mentioned above there are infinitely many ways of choosing this interval, so let's try to make a relatively sensible choice for the end points, namely the 0.16 and 0.84 quantiles:

<p align="center">
  <img width="600" src="images/task_completion_time_n_eq_5000_witinterval.png">
</p>

Ok great, this looks like a much more sensible way of characterizing the data, concretely we can say that a fraction 0.68 of tasks are completed between approximately 5 and 23 minutes.

## Less Data

In the above example, we had lots of data points, therefore our sample looked very similar to the underlying distirbution (which, as we mentioned, we don't have access to). But in practice, we'll often be dealing with small samples (the median task length here for example is 12 minutes, so even if a worker only performed this task for an entire week, we'd still only have approximately 200 datapoints) how does this affect our description statistic?