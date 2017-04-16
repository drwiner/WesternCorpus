Written by David R. Winer
2017 - 04 - 16

An corpus of Western duel scenes in movies are annotated with action instances (action types with entities) for each shot. I wrote a mapping dictionary of these actions to action schemas in a planning domain model, and use this to reconstruct the plot.

1) Used normalized spectral clustering to cluster entities based on their participation in the same argument positions of action types. These clusters are evaluated with MUC and B^3 scoring compared to hand generated clusters.
2) Used hierarchical clustering to group actions via their event relatedness (PMI) using a few different metrics for PMI, such as the Chambers and Jurafsky 08, k-grams, and potential causal linkage using the planning model.