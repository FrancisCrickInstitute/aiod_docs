# Evaluation Widget

!!! warning

    This is a very limited widget with simple functionality. If would like more measures or features, please see our [page on raising issues](../../support/index.md#raising-an-issue)!

This is a very simple widget that just provides access to a few common segmentation measures to compare masks: the [Dice coefficient](https://en.wikipedia.org/wiki/Dice-S%C3%B8rensen_coefficient), [intersection-over-union (IoU)](https://en.wikipedia.org/wiki/Jaccard_index), [Hausdorff distance](https://scikit-image.org/docs/stable/api/skimage.metrics.html#skimage.metrics.hausdorff_distance), and [modified Hausdorf distance](https://doi.org/10.1109/ICPR.1994.576361). If one of your masks is a ground truth (rather than comparing the outputs of two models), then the precision and recall can also be calculated.

These results can be exported to a CSV, or appended to an existing CSV (to e.g. collate results from across multiple model runs).