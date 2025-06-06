# A Small Video-Language Model for Sparse Action Spotting

* Sparse action spotting methods in sports have traditionally been CNN or feature-extractor based

* We introduce a purely token-based pipeline that, when given a video of a sports game, can extract desirable highlights.

* A user should be able to query our system: “Give me all the highlights of free-kicks.”, and receive a response: “A free-kick occurs at (36:09, 36:24)”.

## Repository Structure

- `baseline_inference.ipynb`: Notebook for preliminary inference process.
- `create_finetuning_dataset_colab.ipynb`: Notebook for creating the fine-tuning dataset.
- `evaluation/`: Contains evaluation scripts and metrics.
- `mistral-llm/`: Directory related to experimentation with Mistral.
- `scripts/`: Shell scripts for data processing, finetuning, and evaluation.
- `EECS 545 POSTER.pdf`: Poster presentation summarizing the project.
- `EECS545_Project_Report.pdf`: Paper describing the project.
