Imagine two race scenarios involving 100 equally fast runners, each covering the same distance. In the first scenario, it’s a relay race where each runner must wait for the baton before they can begin. The race’s total time is the sum of each runner’s effort since only one runner moves at a time. In the second scenario, all runners start simultaneously and run their distance independently. While the total distance covered is the same in both cases, the second scenario is 100 times faster because everyone's running at the same time, rather than waiting in line. The total distance travelled by the runners is like the total amount of calculations a computer has to perform to complete a task. This simple difference highlights a powerful concept when considering computations, one of the most significant distinctions lies in whether calculations can be parallelized or are inherently sequential.

Note that we are not discussing scenarios where parallelism or sequential execution is merely an implementation choice for the same underlying calculation — as seen with sorting algorithms. For instance, while
[Bubble Sort](https://www.geeksforgeeks.org/bubble-sort-algorithm/)
is inherently sequential because each pass depends on the previous one,
[Merge Sort](https://www.geeksforgeeks.org/merge-sort/)
can be parallelized by dividing the data into smaller chunks, sorting them independently, and merging the results. Instead, we are focusing on the more fundamental cases where this choice is dictated not by implementation strategy, but by the canonical nature of the computation itself. In other words, there are calculations that, by their very definition, can only be solved step-by-step in a specific order, regardless of how cleverly we try to implement them.

Parallelizable calculations are those that can be broken into smaller, independent tasks that run concurrently. The key requirement is independence—the tasks must not depend on the results of one another.

For example, consider the following operation:

$$
\mathbf{y} = \mathbf{A} \cdot \mathbf{x}
$$

Here, multiplying a matrix $ \mathbf{A}$ by a vector $\mathbf{x}$ involves computing each element of $\mathbf{y}$ independently:

$$
y_i = \sum_{j=1}^n A_{ij} \cdot x_j
$$

Sequential calculations, by contrast, have dependencies between steps that prevent parallel execution. A common example is calculating the Fibonacci sequence:

$$
F(n) = F(n-1) + F(n-2)
$$

Each term depends on the previous two, meaning that we cannot compute $F(n)$ without first computing $F(n-1)$ and $F(n-2) $.

The distinction between parallelizable and sequential computations has far-reaching implications. The rise of AI provides a compelling real-world example of the power of parallelization; the breakthrough in transformer-based architectures, like the ones powering modern AI systems, lies in their ability to leverage parallel computation.

One could imagine, at some level of abstraction, that the human brain is performing a staggering amount of highly parallelized computation to process the immense volume of data it handles. With approximately 86 billion neurons, each capable of forming thousands of connections (synapses) with other neurons, the brain forms a network of trillions of connections. This vast structure processes sensory input, generates thoughts, controls movement, and supports learning and memory—all in real-time. This perspective underscores the power of parallel processing, not just in artificial systems, but as a fundamental principle of efficient computation in the natural world as well.
