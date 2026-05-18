# Seattle Bridge Closure Probability Logic

This document explains the mathematical and programmatic logic used to calculate the probability of a bridge closure in the Seattle Bridge Predictive Engine.

---

## 1. Data Filtering

### Weekday-Only Analysis
Because this is a **commute prediction tool**, we filter the raw dataset to include only **Monday through Friday** events (`dayofweek < 5`). Weekend maritime traffic patterns differ significantly from weekday patterns and would skew commute-focused probabilities.

### Outlier Clipping (Winsorization)
Bridge closures occasionally last far longer than normal due to mechanical failures, emergency situations, or other rare events. These extreme durations (e.g., 51- or 93-minute closures when the median is ~5 minutes) distort the analysis in two ways:

1. **Probability inflation**: A single 93-minute closure spreads its overlap across ~19 consecutive 5-minute bins, artificially inflating the closure probability for all of them.
2. **Expected value distortion**: One extreme event in a sparsely-populated time bin can dominate the mean, making the average unrepresentative of typical conditions.

To address this, we apply **95th-percentile clipping**: we compute the 95th percentile of all closure durations across the dataset (which lands at **~10 minutes**), then cap any closure's `end_time` so that no single event exceeds this duration. This is a standard statistical technique known as *Winsorization* — it preserves the fact that a closure occurred (unlike outright removal) but limits the influence of extreme tail events.

---

## 2. Defining the Time Bins
To create a continuous probability distribution across a 24-hour day, we divide the day into **discrete 5-minute intervals** (bins). 
Since there are 24 hours in a day and 12 bins per hour, this results in exactly **288 bins** per day (e.g., `00:00 - 00:05`, `00:05 - 00:10`, ... `23:55 - 00:00`).

---

## 3. Counting Active Days ($N$)
We must account for the fact that our historical data collection was not always perfectly continuous (e.g., the scraper might have been offline for certain periods).

To prevent artificially diluting the probability by including days where no data could have been collected, we calculate our denominator, $N$, by identifying the exact set of **unique dates** present in the raw dataset (after weekday filtering). This ensures $N$ exclusively represents the active weekdays where the scraper was confirmed to be monitoring bridge activity.

> **Why not use elapsed calendar days?**  
> If the scraper was offline for an entire week, counting those 5 business days in the denominator would treat them as "days with no closures," artificially suppressing the probability. By using only dates that appear in the data, we avoid this bias.

---

## 4. Detecting Overlaps (Duration-Aware)
For every historical bridge closure in our dataset, we have a `start_time` and an `end_time` (post-clipping). The full duration of the closure is used to determine which 5-minute bins it overlaps.

For each of the 288 daily bins, we check if the bin **overlaps** with the closure interval.

*Example:* 
If the bridge was closed from `14:02` to `14:09`:
- The `14:00` bin (14:00 - 14:05) overlaps.
- The `14:05` bin (14:05 - 14:10) overlaps.
- The `14:10` bin (14:10 - 14:15) does **not** overlap.

This means bridges with historically longer closures will naturally produce wider probability distributions, accurately reflecting the greater chance of encountering a delay.

---

## 5. The "Set" Counter (Preventing Double-Counting)
To ensure mathematical rigor, we handle the edge case where two separate closures might happen on the exact same day and overlap the exact same 5-minute bin. 

Instead of keeping a raw integer counter for each bin, we maintain a **Set** of unique dates. If a closure overlaps a bin, we add the `Date` of that closure to the bin's Set. Because Sets only store unique values, if the bridge closed twice in the same 5-minute window on March 14th, March 14th is only counted once.

---

## 6. Final Probability Calculation
For any given 5-minute bin $B_i$, the historical prior probability of the bridge being closed is:

$$ P(\text{Closure}_{i}) = \frac{|\text{Unique Days with an Overlap in } B_i|}{N} $$

If 40 out of 500 active historical weekdays had a closure overlapping the 3:00 PM bin, the probability for that bin is exactly 8%.

---

## 7. Expected Wait Time (Continuous Integral Method)
Rather than sampling at a single point within each 5-minute bin, we compute the **exact continuous integral** of the wait-time function across the entire bin interval.

For each historical closure that overlaps a bin $[a, b]$:
1. Compute the overlap region $[A, B]$ where $A = \max(\text{closure\_start}, a)$ and $B = \min(\text{closure\_end}, b)$.
2. Calculate the area under the wait-time curve (a linearly decreasing function from $(\text{closure\_end} - A)$ down to $(\text{closure\_end} - B)$):

$$ \text{Area} = (B - A) \times \left(\text{closure\_end} - \frac{A + B}{2}\right) $$

3. The average wait time contributed by this closure to the bin is $\frac{\text{Area}}{5}$ (normalizing by the bin width).

This is summed per day, then averaged across all $N$ active weekdays to produce the **Expected Wait Time** — the true mathematical expectation of delay for a commuter arriving uniformly within that 5-minute window.

---

## 8. Average Closure Duration (By Start Bucket)
For each 5-minute bin, we collect all historical closures whose `start_time` falls within that bin and compute the **mean duration** (start to end, post-clipping). This answers: *"If the bridge starts closing right now, how long will it typically last?"*

---

## 9. Confidence Intervals
When plotting the historical probabilities in side-by-side comparisons, we calculate and display a **95% Confidence Interval** for each 5-minute bin. 

Because the probability $p$ is derived from a count of successes (days with a closure) over $N$ trials (active weekdays), it represents a **binomial proportion**. We calculate the standard error (SE) using the normal approximation:

$$ SE = \sqrt{\frac{p(1-p)}{N}} $$

The 95% Confidence Interval is plotted as error bars extending $1.96 \times SE$ above and below the probability point.

---

## 10. Real-Time Bayesian Updating (Inference Engine)
While the historical baseline gives us the static 24-hour curve, the real-time inference engine applies Bayesian logic to update this probability on the fly:
1. **Markov Transitions**: If the bridge is *currently* closed, the probability is overridden by the historical likelihood that a closure lasts longer than 15 minutes.
2. **Hazard Rate**: If the bridge *just* reopened 2 minutes ago, the baseline probability is slashed (multiplied by 0.1) because bridges rarely open back-to-back.
3. **Daily Volume Scaling**: If today has already seen 10 bridge openings by noon (when the historical average is only 5), the baseline probability for the rest of the day is proportionally scaled up to account for the unusually high maritime traffic.
