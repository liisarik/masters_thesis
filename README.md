# masters_thesis
This repository contains the code, data, and evaluation pipeline for CineBias, a dataset of 1,012 stereotypical sentence pairs extracted from Hollywood movie subtitles. The project was developed as part of a master's thesis focused on measuring social biases in language models.

Repository Structure:

scripts/: Main pipeline for parsing .srt subtitle files and extracting stereotypical sentences using keyword-based matching. Includes English keyword lists.

Estonian/: Same pipeline adapted for Estonian subtitles and keywords.

evaluation/: Preprocessing, bias scoring (CrowS-Pairs Score), and results for evaluating language models on:

crowspairs_stereo/: Original CrowS-Pairs dataset.

cinebias/: The CineBias dataset.


This repository accompanies the thesis: Exploring Social Bias in Language
Models through the Lens of Cinema

Language models have revolutionized natural language processing, becoming an integral part of many applications. However, these models
often exhibit societal biases embedded in their training data, raising
concerns about their fairness and ethical deployment. Measuring these
biases usually requires creating datasets with time-consuming human
annotation, which is costly and hard to expand. To address this challenge, we propose a data curation framework and CineBias, a novel
dataset of 1,012 stereotypical sentence pairs covering seven bias categories, extracted from Hollywood movie subtitles with minimal human
intervention. We evaluate the language models BERT, RoBERTa, and
ModernBERT using the CrowS-Pairs Score (CPS) on CineBias, and find
bias levels comparable to established benchmarks (e.g., BERT 61.2%
CPS). This shows that CineBias provides a scalable way to measure
bias. We also demonstrate its applicability to low-resource languages
with an Estonian case study.

Full thesis can be read from here: https://thesis.cs.ut.ee/e19176d9-7f39-4298-81f1-622a0c5c03c0



